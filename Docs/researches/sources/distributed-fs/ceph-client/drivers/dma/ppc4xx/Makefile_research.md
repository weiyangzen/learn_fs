# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/Makefile

## Purpose
This Makefile connects the PPC4xx DMA subdirectory to Kbuild. It builds the `adma.o` object when `CONFIG_AMCC_PPC440SPE_ADMA` is enabled.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_AMCC_PPC440SPE_ADMA) += adma.o` is the only build rule and expresses a direct config-to-object dependency.
- The SPDX header declares GPL-2.0-only licensing for the build metadata.

## Control Flow
There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_AMCC_PPC440SPE_ADMA`; when it is `y` or `m`, `adma.o` is included in the directory's built-in or module object list according to standard Kbuild semantics.

## State and Persistence
No runtime state exists. The only persistent behavior is build graph selection derived from kernel configuration.

## Dependencies and Integration Points
The file depends on the surrounding Linux Kbuild system and on a sibling `adma.c`/`adma.o` implementation in the same `ppc4xx` directory. It integrates with the architecture/platform DMA configuration symbol `CONFIG_AMCC_PPC440SPE_ADMA`.

## Risks and Edge Cases
- If `CONFIG_AMCC_PPC440SPE_ADMA` is selectable but `adma.c` or its dependencies are missing, the build will fail.
- No additional objects are listed, so any helper source introduced for PPC4xx ADMA would need this Makefile updated.
- The file does not declare module-specific flags or composite objects; all complexity is expected to live in `adma.o`.

## Test Signals
Build testing should cover `CONFIG_AMCC_PPC440SPE_ADMA=y`, `m`, and unset where applicable, and confirm the resulting object is included or omitted as expected.
