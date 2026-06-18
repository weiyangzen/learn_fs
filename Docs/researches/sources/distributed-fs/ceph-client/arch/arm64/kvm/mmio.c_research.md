# sources/distributed-fs/ceph-client/arch/arm64/kvm/mmio.c

## Purpose
This file decodes and completes guest MMIO abort handling for ARM64 KVM. It converts register values to/from MMIO byte buffers, routes MMIO to in-kernel emulation or userspace, handles returns from userspace emulation, and deals with no-valid-syndrome or special LD/ST64B-style exits.

## Important APIs, Types, and Functions
- `kvm_mmio_write_buf()` and `kvm_mmio_read_buf()` marshal 1, 2, 4, or 8 byte accesses.
- `kvm_handle_mmio_return()` completes reads after in-kernel or userspace emulation and advances the PC.
- `io_mem_abort()` is called when a stage-2 abort targets an IPA outside RAM or otherwise needs MMIO handling.
- `kvm_pending_external_abort()` detects whether an exception was already injected before MMIO completion.

## Control Flow
`io_mem_abort()` first checks whether the data abort syndrome is valid. If not, protected guests get a SEA; configured VMs can exit with `KVM_EXIT_ARM_NISV`; otherwise KVM returns `-ENOSYS`. Certain load/store type encodings are sent to userspace as `KVM_EXIT_ARM_LDST64B`.

For valid syndromes, the handler decodes write/read, access size, and target register. Writes convert guest register data to host byte order, trace the access, and try `kvm_io_bus_write()`. Reads trace an unsatisfied read and try `kvm_io_bus_read()`. It then fills `run->mmio`, marks `vcpu->mmio_needed`, completes immediately when the in-kernel bus handled the access, or exits to userspace with `KVM_EXIT_MMIO`.

`kvm_handle_mmio_return()` ignores already-handled or aborted accesses, clears `mmio_needed`, reads returned data for load instructions, applies sign extension and 32-bit masking, converts host data back to guest format, stores the destination register, traces the completed read, and increments the PC.

## State and Persistence
State is stored in `vcpu->mmio_needed`, `vcpu->run->mmio`, `vcpu->stat.mmio_exit_kernel`, `vcpu->stat.mmio_exit_user`, guest registers, and the guest PC. It also respects pending exception flags so an externally injected abort is not overwritten by MMIO completion.

## Dependencies and Integration Points
It depends on KVM data-abort syndrome helpers, MMIO bus APIs, tracepoints, `struct kvm_run` userspace ABI fields, guest/host data conversion helpers, and fault injection for protected/no-syndrome cases. `mmu.c` calls `io_mem_abort()` when a faulting IPA is not backed by a memory slot.

## Risks and Edge Cases
Risks include incorrect sign extension, wrong 32-bit register truncation, treating invalid syndrome accesses as emulatable, and completing MMIO after an exception has been injected. Special LD/ST64B handling is punted to userspace because full emulation cannot be inferred from ordinary syndrome fields.

## Test Signals
Exercise 8/16/32/64-bit MMIO reads/writes, sign-extending loads, AArch32 register truncation, in-kernel device emulation, userspace MMIO exits, NISV exits, protected VM invalid syndrome paths, and LD/ST64B exits. Tracepoints should reflect write, unsatisfied read, and completed read paths.
