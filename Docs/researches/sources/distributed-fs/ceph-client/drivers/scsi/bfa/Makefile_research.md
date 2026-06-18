# sources/distributed-fs/ceph-client/drivers/scsi/bfa/Makefile

## Purpose

This Makefile integrates the Brocade/BFA Fibre Channel SCSI driver into the kernel build. It defines the composite `bfa.o` object that is built when `CONFIG_SCSI_BFA_FC` is enabled and lists the constituent object files that implement the BFA driver stack.

## Important Build Targets

`obj-$(CONFIG_SCSI_BFA_FC) := bfa.o` tells kbuild to include the `bfa` driver object according to the `SCSI_BFA_FC` Kconfig setting. The `bfa-y` lists aggregate these objects into `bfa.o`: driver front-end files (`bfad.o`, `bfad_im.o`, `bfad_attr.o`, `bfad_debugfs.o`, `bfad_bsg.o`), IOC and hardware support (`bfa_ioc.o`, `bfa_ioc_cb.o`, `bfa_ioc_ct.o`, `bfa_hw_cb.o`, `bfa_hw_ct.o`), Fibre Channel services (`bfa_fcs.o`, `bfa_fcs_lport.o`, `bfa_fcs_rport.o`, `bfa_fcs_fcpim.o`, `bfa_fcbuild.o`), and lower-level port/FCP/core/service modules (`bfa_port.o`, `bfa_fcpim.o`, `bfa_core.o`, `bfa_svc.o`).

## Control Flow

There is no runtime control flow in this file. At build time, kbuild evaluates `CONFIG_SCSI_BFA_FC`, compiles the listed source files to objects, and links them into a single `bfa.o` module/built-in object according to the broader kernel configuration.

## State And Persistence Behavior

The file does not maintain runtime state or persistent data. Its build-state effect is deterministic: enabling the config includes all listed objects in the BFA driver; disabling it omits the composite object.

## Dependencies And Integration Points

The Makefile depends on Linux kbuild syntax and the existence of all listed `.c` files in the same directory. It integrates with the SCSI subsystem through the corresponding Kconfig option and with any module/built-in rules inherited from the surrounding kernel tree.

## Risks And Edge Cases

Missing or renamed object files will break the build. Adding a source file without updating `bfa-y` can silently omit code from the driver. Reordering generally should not matter for normal kernel object aggregation, but unresolved symbol dependencies or initcall/linker-section behavior should still be considered when making nontrivial build changes.

## Test Signals

The primary test is a kernel build with `CONFIG_SCSI_BFA_FC=y` and/or `m`, plus a disabled-config build to ensure the object is omitted. Build logs should show all listed BFA objects compiled and linked into `bfa.o` without missing-object or unresolved-symbol errors.
