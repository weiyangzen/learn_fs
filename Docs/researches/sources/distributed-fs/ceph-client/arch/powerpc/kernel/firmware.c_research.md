# sources/distributed-fs/ceph-client/arch/powerpc/kernel/firmware.c

## Purpose

`firmware.c` holds small shared PowerPC firmware feature state. On PPC64 it exports `powerpc_firmware_features`, and on pseries or KVM guest builds it detects whether the kernel is running as a KVM guest by inspecting the device tree `/hypervisor` node. The file is intentionally small but forms a common integration point for firmware capability checks and static-branch optimized guest checks.

## Important APIs, types, and functions

The PPC64 global `unsigned long powerpc_firmware_features __read_mostly` is exported with `EXPORT_SYMBOL_GPL`, allowing other GPL kernel code to check discovered firmware features. With `CONFIG_PPC_PSERIES` or `CONFIG_KVM_GUEST`, `DEFINE_STATIC_KEY_FALSE(kvm_guest)` declares a jump-label static key, also exported GPL. `check_kvm_guest` is a `core_initcall`, scheduled before `kvm_guest_init`, and enables the `kvm_guest` static branch when `/hypervisor` is compatible with `"linux,kvm"`.

## Control flow

Initialization is straightforward. `check_kvm_guest` calls `of_find_node_by_path("/hypervisor")`; if the node is missing it returns without changing state. If present, it calls `of_device_is_compatible` and enables the static branch with `static_branch_enable(&kvm_guest)` for `"linux,kvm"`. It releases the device-node reference with `of_node_put` and returns success. Since it is a core initcall, later KVM guest initialization can use the static key cheaply.

## State and persistence behavior

`powerpc_firmware_features` is read-mostly global state populated elsewhere in the architecture firmware discovery path. `kvm_guest` is a static key: once enabled, patched branch sites in other code can use the optimized true path without repeated device-tree checks. The only persistence handled directly here is the lifetime of the static global state; device-tree node references are not retained.

## Dependencies and integration points

Dependencies include `<asm/firmware.h>` for firmware feature declarations, `<asm/kvm_guest.h>` for the static key declaration, Linux OF helpers, jump-label static keys, and module export infrastructure. Integration points are pseries and generic KVM guest code that check `kvm_guest`, plus any PPC64 code reading `powerpc_firmware_features`.

## Risks and invariants

The main invariant is init ordering: the static key must be enabled before guest-specific initialization uses it, which is why the file uses `core_initcall(check_kvm_guest)`. Device-tree compatibility string accuracy determines detection. If firmware describes a KVM guest differently, this path will leave the key disabled. The node reference is correctly dropped; changes should preserve that ownership.

## Test signals

Useful signals are pseries/KVM guest boots where `/hypervisor` exists with `linux,kvm`, non-KVM pseries boots where it does not, and module or built-in users of `kvm_guest` seeing patched static-branch behavior. Build coverage should include PPC64, pseries, KVM guest, and configurations where the KVM guest block is not compiled.
