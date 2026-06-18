# File Research: sources/block-storage/lvm2/lib/format_text/text_export.h

## Summary
Declares formatter helpers used by text metadata export code.

## Main Contents
Provides convenience macros `outsize`, `outhint`, `outfc`, `outf`, and `outnl` that return failure to the caller when output operations fail. Declares formatted output helpers, config-node output, segment-area output, indentation controls, and newline output.

## Risks And Invariants
The output functions are annotated with `printf` format checking and `warn_unused_result`; callers are expected to propagate write failures immediately through the macros.
