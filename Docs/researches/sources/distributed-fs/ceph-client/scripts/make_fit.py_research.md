<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/make_fit.py -->
# sources/distributed-fs/ceph-client/scripts/make_fit.py

## Purpose

`make_fit.py` builds a U-Boot-compatible FIT image containing a kernel, optional ramdisk, and many DTBs. It can compress image payloads, deduplicate DTBs, decompose composite DTBs created by `fdtoverlay`, and optionally convert embedded data into external FIT data.

## Important APIs, Types, and Functions

Important functions are `parse_args()`, `setup_fit()`, `write_kernel()`, `write_ramdisk()`, `finish_fit()`, `compress_data()`, `compress_dtb()`, `output_dtb()`, `process_dtb()`, `_process_dtbs()`, `build_fit()`, and `run_make_fit()`. `COMP_TOOLS` maps compression names to file extensions and command fallback lists. It uses `libfdt.FdtSw` for writing and `libfdt.FdtRo` for reading DTB model/compatible metadata.

## Control Flow

The main path parses FIT metadata, writes the root and `/images`, compresses and embeds the kernel, embeds an uncompressed ramdisk if supplied, processes DTBs, writes `/configurations`, packs the FDT, writes the output file, and optionally runs `mkimage -E -F` to externalize payload data. DTB processing first reads root properties, optionally uses the `.dtb.cmd` file to split composite DTBs into base/overlay inputs, compresses unique DTB files in parallel, and emits each unique file once.

## State and Persistence Behavior

The script persists only the requested FIT output file. During compression it creates temporary files and multiprocessing worker state. The FIT contains a generation timestamp, payload bytes or external data metadata, per-DTB nodes, and configurations referencing one or more `fdt-*` nodes.

## Dependencies and Integration Points

It depends on Python `libfdt`, external compression commands such as `gzip`, `zstd`, `xz`, `lz4`, and optional `mkimage`. It integrates with kernel DTB build output, particularly `.cmd` files containing `scripts/dtc/fdtoverlay` commands, and with bootloaders that understand FIT.

## Risks and Edge Cases

Compression uses `subprocess.call()` but does not inspect non-zero exit status if the tool exists, so failed compressors can produce empty or bad payloads. Composite DTB decomposition assumes command-line structure around `-i`. Missing root `model` or `compatible`, missing `.cmd` files, duplicate basenames, huge payloads, absent compression tools, and external FIT conversion failures are important edges.

## Test Signals

Useful tests build FITs with no compression and each supported compressor, verify DTB deduplication and composite decomposition, run `dumpimage`/`fdtdump` on the output, check external FIT totalsize reporting, and assert failures for missing kernel, bad DTB, missing compressor, malformed `.cmd`, and absent `mkimage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/make_fit.py -->
