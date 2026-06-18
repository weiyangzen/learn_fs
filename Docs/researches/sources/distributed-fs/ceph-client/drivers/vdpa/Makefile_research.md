# sources/distributed-fs/ceph-client/drivers/vdpa/Makefile

Purpose: top-level vDPA build routing.

Important APIs/types/functions: maps Kconfig symbols to objects/subdirectories: `vdpa.o`, `vdpa_sim/`, `vdpa_user/`, `ifcvf/`, `mlx5/`, `virtio_pci/`, `alibaba/`, `solidrun/`, `pds/`, and `octeon_ep/`.

Control flow: kbuild descends into vendor subdirectories only when the associated config symbol is enabled.

State and persistence: no runtime state; build graph only.

Dependencies and integration: integrates Kconfig with kbuild object generation for the vDPA subsystem.

Risks: symbol/object mismatches silently omit drivers or cause link failures. The file assumes subdirectory Makefiles provide module composition.

Test signals: `make drivers/vdpa/` with each relevant config enabled, and module list checks for expected `.ko` names.
