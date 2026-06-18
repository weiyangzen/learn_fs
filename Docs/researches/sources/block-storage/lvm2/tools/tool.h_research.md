# File Research: sources/block-storage/lvm2/tools/tool.h

## Purpose
`tool.h` is a small common include header for LVM2 tool sources.

## Contents
It includes allocation helpers, libdevmapper, generic utility helpers, and `<unistd.h>`.

## Integration Notes
The header comment says most source files should include `tool.h`, `lib.h`, or `dmlib.h`. It provides basic dependencies rather than command-specific declarations.
