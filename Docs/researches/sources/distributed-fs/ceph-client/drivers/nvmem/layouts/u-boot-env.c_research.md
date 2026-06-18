# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.c

Purpose: NVMEM layout driver for U-Boot environment images. It validates the environment CRC, interprets single, redundant, and Broadcom image headers, and registers each `name=value` entry as an NVMEM cell.

Important APIs/types/functions: `u_boot_env_parse()` is exported for providers; `u_boot_env_add_cells()` wires the parser into `struct nvmem_layout`; `u_boot_env_parse_cells()` mutates the read buffer into C strings and calls `nvmem_add_one_cell()`; `u_boot_env_read_post_process_ethaddr()` converts an `ethaddr` string to six bytes and applies index-based MAC increments. Image structs describe single CRC-only, redundant CRC+mark, and Broadcom magic/len/CRC layouts.

Control flow: probe installs `layout->add_cells` and registers the layout. Parsing chooses offsets from the matched format, reads either `env-size` or the full NVMEM size, computes little-endian CRC32 over the payload, NUL-terminates the buffer, then walks NUL-separated variables until a missing `=` or empty variable stops parsing.

State/persistence: no persistent state beyond dynamically registered NVMEM cells. It allocates a temporary full-image buffer and uses devm allocations for cell names; the underlying provider owns the actual nonvolatile storage.

Dependencies/integration: depends on the NVMEM provider/layout APIs, OF compatibles `u-boot,env`, redundant variants, and `brcm,env`; optionally links cells to child OF nodes by variable name. The top-level MTD-backed provider in `drivers/nvmem/u-boot-env.c` calls the exported parser.

Risks: CRC endianness is read through a cast rather than `le32_to_cpup()`, so this assumes little-endian interpretation consistent with the target build. Parsing writes NULs into the temporary buffer, so callers must provide writable data. Malformed environments stop cell discovery silently after a variable without `=`.

Test signals: exercise valid and invalid CRC images for all three formats; verify `env-size` truncation, NVMEM read short-read handling, `ethaddr` post-processing with indexed aliases, and OF child-cell association.
