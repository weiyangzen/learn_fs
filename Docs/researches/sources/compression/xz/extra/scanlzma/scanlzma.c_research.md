<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/extra/scanlzma/scanlzma.c -->
# sources/compression/xz/extra/scanlzma/scanlzma.c

Purpose: scans stdin for a legacy LZMA-alone header and emits the selected embedded stream to stdout.

Important APIs/types/functions: `find_lzma_header` checks property byte, dictionary-size byte constraints, and unknown-size/zero-size patterns; `main` parses stream index, scans 4096-byte blocks, writes from match offset, then copies the rest of stdin.

Control flow: require `numlzma` argument, read full blocks with `fread`, inspect offsets up to `BUFSIZE - 23`, decrement requested match count until target, then stream remaining bytes.

State and persistence: no persistent state; output is stdout.

Dependencies and integration: standalone GPL utility for firmware/recovery workflows, intended to pipe into `lzma -d`.

Risks: block-boundary matches can be missed because scanning does not overlap buffers. Header heuristic is narrow (`0x5d`) and can false-positive/false-negative. It returns failure if no target stream is found.

Test signals: run on firmware fixtures with known embedded LZMA offsets; compare extracted decompressed content to expected strings/files.
<!-- END_FILE_RESEARCH: sources/compression/xz/extra/scanlzma/scanlzma.c -->
