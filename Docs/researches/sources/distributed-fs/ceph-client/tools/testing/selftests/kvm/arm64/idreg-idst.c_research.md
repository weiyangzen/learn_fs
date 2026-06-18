# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/idreg-idst.c

Purpose: this selftest verifies FEAT_IDST-handled sysregs that depend on more than FEAT_AA64 trap as SYS64 accesses, rather than unexpectedly undefining or being directly readable, when the guest lacks related features.

Important APIs and functions: macros `__check_sr_read()` and `check_sr_read()` read selected sysregs and assert that `guest_sys64_handler()` ran and `guest_undef_handler()` did not. Guest `guest_code()` checks `CCSIDR2_EL1`, `SMIDR_EL1`, and `GMID_EL1`. Host `test_guest_feat_idst()` installs sync handlers for `ESR_ELx_EC_SYS64` and `ESR_ELx_EC_UNKNOWN`.

Control flow: `main()` disables default VGIC, probes `ID_AA64MMFR2_EL1.IDS`, skips if FEAT_IDST is absent, then creates a VM without MTE/SME/CCIDX and runs the guest. Each sysreg read should trap to the SYS64 handler, which advances PC and records `sys64=true`.

State and persistence: volatile guest booleans `sys64` and `undef` record which handler ran. No durable state is stored.

Dependencies and integration points: depends on arm64 ID register fields, KVM sysreg trap handling, descriptor-table sync handlers, and default-VGIC disabling to keep the VM minimal.

Risks: the test assumes the created VM lacks the features tied to the tested registers. Feature exposure changes may require updating the register list or setup.

Test signals: guest assertions fail if any tested register UNDEFs or reads without a SYS64 trap. Host fails on unknown ucalls.
