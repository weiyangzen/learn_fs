# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/Makefile

Purpose: defines the build composition for x86 CPU microcode loading support.

Important APIs and flow: `microcode-y := core.o` builds the common loader core. `obj-$(CONFIG_MICROCODE) += microcode.o` includes the aggregate object when microcode support is enabled. Vendor-specific objects are included conditionally: `intel.o` for `CONFIG_CPU_SUP_INTEL` and `amd.o` for `CONFIG_CPU_SUP_AMD`.

State and persistence: no runtime state; it controls which microcode implementation objects are linked.

Dependencies and integration: ties CPU vendor support Kconfig to the microcode subsystem used by CPU bring-up and mitigation code, including Intel initialization that reads current microcode revisions.

Risks and test signals: wrong object selection can break vendor microcode loading or leave common code without a vendor backend. Signals are Kconfig build matrix coverage and boot-time microcode update logs on Intel-only, AMD-only, and mixed-capability configurations.
