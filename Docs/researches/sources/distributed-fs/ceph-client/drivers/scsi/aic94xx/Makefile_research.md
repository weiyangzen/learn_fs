# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Makefile

Purpose: Kbuild recipe for the composite `aic94xx` kernel module/object.

Important APIs/types/functions: `ccflags-$(CONFIG_AIC94XX_DEBUG)` defines `ASD_DEBUG` and `ASD_ENTER_EXIT`. `obj-$(CONFIG_SCSI_AIC94XX)` builds `aic94xx.o`. `aic94xx-y` links init, hardware interface, register access, SDS/flash, sequencer, dump, SCB, device, TMF, and task files.

Control flow: no runtime flow; Kbuild evaluates the object list and compile flags.

State and persistence: build graph state is derived from `.config`; no runtime state.

Dependencies and integration: this file is the folder-level integration point joining the driver’s PCI/libsas core, hardware bring-up, firmware/SDS parsing, command building, task management, and debug dumping into one module.

Risks and test signals: object-list drift causes unresolved symbols such as `asd_execute_task()`, `asd_read_ocm()`, `asd_init_seqs()`, or TMF callbacks. Build tests with debug enabled/disabled and module/built-in variants are the primary signal.
