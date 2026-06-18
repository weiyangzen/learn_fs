# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/Makefile

## Purpose
This Makefile defines how the Linux kernel builds the Adaptec `aic7xxx` Fast through Ultra160 driver and `aic79xx` Ultra320 driver families, including platform glue, optional EISA/PCI front ends, optional pretty register printers, and generated sequencer/register headers from `aicasm`.

## Important APIs, Types, And Functions
Kbuild targets are `obj-$(CONFIG_SCSI_AIC7XXX) += aic7xxx.o` and `obj-$(CONFIG_SCSI_AIC79XX) += aic79xx.o`. `aic7xxx-y` includes core, 93cx6, OSM, proc, and conditional EISA/PCI/pretty-print objects. `aic79xx-y` includes core, PCI, OSM, proc, OSM PCI, and optional pretty-print objects. The Makefile declares generated sequence/register headers and register print files as clean targets and explicit prerequisites for driver objects.

## Control Flow
When firmware build configs are enabled, `aicasm` is built from `aicasm/*.[chyl]` and invoked with include, register, optional pretty-print, output, and sequence inputs. When firmware build configs are disabled, shipped generated register print C files are used for pretty printing. `subdir += aicasm` ensures clean descends into the assembler directory.

## State And Persistence Behavior
The Makefile persists no runtime state. Build artifacts are generated in the object tree and removed by `make clean`. Conditional generated-file variables act as build graph state based on kernel config.

## Dependencies And Integration Points
This file integrates with Kbuild, `CONFIG_SCSI_AIC7XXX`, `CONFIG_SCSI_AIC79XX`, EISA/PCI config symbols, register pretty-print configs, firmware build configs, and the local `aicasm` tool. It includes `aic7770.c` and `aic7770_osm.c` only when `CONFIG_EISA` is enabled.

## Risks
Generated headers are prerequisites for many objects; stale or missing `aicasm` outputs can break broad builds. Pretty-print generation depends on OSM header names. `WARNINGS_BECOME_ERRORS` can turn compiler warning drift into build failures.

## Test Signals
Useful signals include successful `make M=drivers/scsi/aic7xxx` under AIC7XXX and AIC79XX configs, with and without EISA/PCI and pretty-print options; clean removal of generated files; correct `aicasm` rebuild when sequence/register inputs change; and no missing generated header errors in incremental builds.
