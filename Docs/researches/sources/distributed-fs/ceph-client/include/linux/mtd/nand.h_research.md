# sources/distributed-fs/ceph-client/include/linux/mtd/nand.h

## Purpose

Defines the generic NAND device model used by raw NAND, SPI NAND, and other NAND-like layers, including memory organization, positions, page I/O requests, ECC engine abstraction, bad-block table state, and MTD bridge helpers.

## Important APIs, Types, and Functions

Key types include `nand_memory_organization`, `nand_pos`, `nand_page_io_req`, `nand_ecc_props`, `nand_ops`, `nand_ecc_engine`, `nand_device`, and `nand_io_iter`. Public helpers cover ECC engine init/cleanup/prepare/finish, software/on-die/on-host engine lookup, request tweaking, device init/register/unregister, offset/position conversions, page/block iterators, BBT operations, and MTD erase/max-bad-block bridge functions.

Source-visible symbols include structs: `struct nand_device;`, `struct nand_memory_organization`, `struct nand_row_converter`, `struct nand_pos`, `struct nand_page_io_req`, `struct nand_pos pos;`, `struct nand_ecc_props`, `struct nand_bbt`, `struct nand_ops`, `struct nand_ecc_context`, `struct nand_ecc_props conf;`, `struct nand_ecc_engine_ops`; enums: `enum nand_page_io_req_type`, `enum nand_page_io_req_type type;`, `enum nand_ecc_engine_type`, `enum nand_ecc_placement`, `enum nand_ecc_algo`, `enum nand_ecc_engine_type engine_type;`, `enum nand_ecc_placement placement;`, `enum nand_ecc_algo algo;`, `enum nand_ecc_engine_integration`, `enum nand_ecc_engine_integration integration;`; typedefs: none visible in this header; prototypes: `void of_get_nand_ecc_user_config(struct nand_device *nand);`, `int nand_ecc_init_ctx(struct nand_device *nand);`, `void nand_ecc_cleanup_ctx(struct nand_device *nand);`, `bool nand_ecc_is_strong_enough(struct nand_device *nand);`, `int nand_ecc_register_on_host_hw_engine(struct nand_ecc_engine *engine);`, `int nand_ecc_unregister_on_host_hw_engine(struct nand_ecc_engine *engine);`, `void nand_ecc_put_on_host_hw_engine(struct nand_device *nand);`, `void nand_ecc_cleanup_req_tweaking(struct nand_ecc_req_tweak_ctx *ctx);`, `return container_of(mtd, struct nand_device, mtd);`, `return nanddev_target_size(nand) * nanddev_ntargets(nand);`, `void nanddev_cleanup(struct nand_device *nand);`, `return mtd_device_register(&nand->mtd, NULL, 0);`, `return mtd_device_unregister(&nand->mtd);`, `return mtd_get_of_node(&nand->mtd);`; representative macros: `__LINUX_MTD_NAND_H`, `NAND_MEMORG`, `NAND_ECCREQ`, `NAND_ECC_MAXIMIZE_STRENGTH`, `nanddev_io_for_each_page`, `nanddev_io_for_each_block`.

## Control Flow

Specialized NAND layers fill memorg and ECC requirements, call `nanddev_init()`, then expose MTD callbacks. MTD requests are split by `nanddev_io_for_each_page()` or block iterators into `nand_page_io_req` objects. ECC engines prepare a request before I/O and finish it after I/O, while bad-block helpers gate erase/markbad/isbad operations.

## State and Persistence Behavior

Runtime state is embedded in `nand_device`: MTD core object, memory geometry, ECC defaults/requirements/user config/context, row conversion shifts, BBT cache, and low-level ops. Request tweak contexts may allocate bounce buffers to adapt partial/OOB requests.

## Dependencies and Integration Points

It depends on MTD core and is included by raw NAND and SPI NAND layers. It also integrates with device tree ECC configuration and optional software/on-host/on-die ECC engines.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`.

## Risks and Edge Cases

Offset-to-position math must match geometry, especially multi-target/LUN/plane devices. ECC engine selection and request tweaking can change buffers; callers must restore requests and propagate bitflip/ECC errors correctly.

## Test Signals

Unit-test position conversions, page/block iterators, ECC config negotiation, BBT status transitions, bad-block MTD bridge behavior, and partial data/OOB request tweaking.

Source read signal: 1144 lines, 34539 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
