# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/Makefile

Purpose: describes how the ATTO ExpressSAS RAID driver is built from its component objects when `CONFIG_SCSI_ESAS2R` is enabled.

Important APIs/types/functions: sets `obj-$(CONFIG_SCSI_ESAS2R) += esas2r.o` and composes `esas2r-objs` from `esas2r_log.o`, `esas2r_disc.o`, `esas2r_flash.o`, `esas2r_init.o`, `esas2r_int.o`, `esas2r_io.o`, `esas2r_ioctl.o`, `esas2r_targdb.o`, `esas2r_vda.o`, and `esas2r_main.o`.

Control flow: no runtime control flow. Kbuild uses the config-selected `obj-*` assignment to build either a module or built-in object, then links the listed component objects into the composite `esas2r.o`.

State and persistence behavior: build metadata only. The file creates no runtime state; it determines object inclusion and link composition during kernel builds.

Dependencies and integration points: integrates with `Kconfig` via `CONFIG_SCSI_ESAS2R` and with the ESAS2R source files that implement logging, discovery, firmware, initialization, interrupts, I/O, ioctls, target database, VDA management, and module entry points. Link ordering can matter for initialization data, exported/local symbols, and dead-code diagnostics.

Risks and test signals: risks are missing object files, stale object names after refactors, and link failures if the composite omits a translation unit that provides referenced symbols. Test signals include `make M=drivers/scsi/esas2r` or full kernel builds for `m` and `y`, modpost symbol checks, and smoke-loading the module on compatible PCI configurations.
