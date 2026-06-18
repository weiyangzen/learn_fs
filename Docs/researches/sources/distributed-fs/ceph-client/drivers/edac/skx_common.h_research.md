# sources/distributed-fs/ceph-client/drivers/edac/skx_common.h

Purpose: `skx_common.h` defines the shared contract for Intel SKX-family EDAC code: constants, topology objects, decode results, resource descriptions, retry-read-log layouts, and exported common helper prototypes.

Important APIs/types/functions: major definitions include `GET_BITFIELD()`, channel/DIMM maxima, DIMM-present and MCE memory-error masks, `enum rrl_mode`, `struct reg_rrl`, `struct skx_dev`, `struct decoded_addr`, `struct pci_bdf`, `struct res_config`, callback typedefs, and prototypes for ADXL, mapping, DIMM, MCE, registration, cleanup, and debug setup helpers.

Control flow: front-end drivers instantiate `struct res_config`, discover and populate `struct skx_dev`, call `skx_register_mci()`, install decode callbacks with `skx_set_decode()`, and rely on common MCE reporting.

State and persistence: all state described here is in-memory. `struct skx_dev` uses a flexible IMC array and nested channel/DIMM data that live until `skx_remove()`.

Dependencies/integration: Linux bit helpers and x86 MCE definitions, with EDAC users including `edac_module.h`. It models Intel server DDR/HBM/DDR5/NVDIMM/2LM and ADXL semantics.

Risks: structure and enum changes affect several drivers; maximum dimensions must not override runtime per-controller counts; physical/logical MC mapping is subtle when firmware hides controllers.

Test signals: compile all users, then exercise DDR-only, HBM, DDR5, NVDIMM, 1LM/2LM, and hidden-controller systems.
