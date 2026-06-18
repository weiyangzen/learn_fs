# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_emulation_test.c

Purpose: Tests KVM instruction emulation for selected instructions executed by L2 under nested virtualization, including use of the forced-emulation prefix.

Important APIs/types/functions: `struct emulated_instruction` describes instruction bytes and expected length; `instructions[]` is the test matrix; `kvm_fep[]` is the forced-emulation prefix; `l2_guest_code[]` is dynamically populated; `get_instruction_length()` and `guest_code()` drive execution. It uses nested VMX/SVM helpers and KVM forced emulation.

Control flow: The guest/L1 copies each instruction after the forced-emulation prefix into the L2 code buffer, launches L2, and expects KVM to emulate the instruction or produce the correct nested exit. It repeats through the instruction matrix and reports completion through ucalls.

State and persistence behavior: L2 code bytes are mutable guest memory. Nested control state persists across individual instruction runs within the same VM.

Dependencies and integration points: Depends on KVM nested virtualization, emulator support for the selected instructions, and the selftest forced-emulation prefix contract.

Risks and maintenance notes: Dynamic code generation requires exact instruction lengths and writable/executable guest memory. Adding instructions requires careful expected-length and exit updates.

Test signals: Passing means selected instructions emulate correctly in nested context, including forced-emulation paths. Failures point to nested emulator, instruction-length, or exit-propagation regressions.
