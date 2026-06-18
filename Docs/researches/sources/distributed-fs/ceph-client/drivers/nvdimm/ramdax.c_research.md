# sources/distributed-fs/ceph-client/drivers/nvdimm/ramdax.c

Purpose: Provides a RAM-backed libnvdimm provider for e820 type-12 memory and OF `pmem-region`, including an emulated label area at the end of each resource. It lets RAM-like persistent ranges participate in namespace label workflows.

Important APIs and flow: `ramdax_probe()` registers an NVDIMM bus with `ramdax_ctl()`, then either scans OF resources or legacy persistent-memory resources. `ramdax_register_dimm()` maps the last 128 KiB as a label area, creates an `nvdimm` with label config commands, and registers a one-mapping PMEM region through `ramdax_register_region()`. The control path handles `ND_CMD_GET_CONFIG_SIZE`, `GET_CONFIG_DATA`, and `SET_CONFIG_DATA` by bounds-checking and copying from/to the mapped label area.

State and persistence behavior: `struct ramdax_dimm` stores the created `nvdimm` and mapped label area. The label area lives in the physical resource and is treated as persistent namespace metadata; region capacity excludes `LABEL_AREA_SIZE`.

Dependencies and integration points: Uses libnvdimm bus, DIMM, region, and ndctl command plumbing; e820 resource walking; OF matching; `memremap()` with write-back mapping; and synthetic interleave-set cookies.

Risks and test signals: `ramdax_probe_of()` notes a FIXME for unregistering already-created DIMMs after a later resource fails. Tests should cover label bounds, command mask enforcement, multi-resource OF cleanup, too-small resources, e820 scanning, and persistence of label writes across namespace reprobe.
