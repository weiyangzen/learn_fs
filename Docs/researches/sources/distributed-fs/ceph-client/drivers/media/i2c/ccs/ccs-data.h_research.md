# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.h

## Purpose
`ccs-data.h` defines the in-memory representation of parsed CCS static data and declares `ccs_data_parse()`. It is the contract between firmware parsing, register access, and core sensor setup.

## Important APIs, Types, and Functions
Important types include `struct ccs_data_block_version`, `struct ccs_reg`, `struct ccs_if_rule`, `struct ccs_frame_format_descs`, `struct ccs_pdaf_readout`, `struct ccs_rule`, PDAF pixel-location descriptor/group structs, and `struct ccs_data_container`. `struct ccs_data_container` aggregates sensor and module register arrays, rule arrays, PDAF data, license data, end marker state, and the opaque `backing` allocation.

## Control Flow
The header has no control flow. Runtime flow is: `ccs-core.c` loads firmware, `ccs_data_parse()` fills a `ccs_data_container`, `ccs-reg-access.c` reads static read-only register arrays, and `ccs-core.c` writes parsed manufacturer-specific register arrays after power-on.

## State and Persistence Behavior
All fields are memory state only. Pointer fields are owned by `backing`; freeing `backing` invalidates registers, rules, frame descriptors, PDAF data, and license pointers. The parser zeroes the container on failure, so callers can use a zeroed container to mean no usable static data.

## Dependencies and Integration Points
The header depends only on kernel integer types plus forward declaration of `struct device`. It integrates with CCS firmware loading, static register lookup, manufacturer-specific register programming, and any future code that consumes PDAF or rule data.

## Risks and Edge Cases
Consumers must honor counts before dereferencing arrays and must not independently free nested pointers. The typo `num_pixel_desc_grups` is part of the public in-tree struct field. License data is length-delimited, not guaranteed string-terminated. Rule contents may be absent even when `num_*_rules` is nonzero depending on parse block content.

## Test Signals
Compile-time users should include this header without circular dependencies. Runtime tests should validate parser output counts/pointers, backing lifetime across probe/remove, static read-only register lookup, and manufacturer-register writes from both sensor and module containers.
