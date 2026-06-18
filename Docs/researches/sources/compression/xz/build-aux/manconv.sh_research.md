# sources/compression/xz/build-aux/manconv.sh

## Purpose
This wrapper converts groff man-page input to ASCII, UTF-8, PostScript, or PDF, with consistent font and paragraph spacing for print formats.

## Important Control Flow
It reads `FORMAT` and optional `PAPER` arguments, defines `FONT=11`, `PD=0.8`, and a `sed` script that injects or normalizes `.PD`. A case statement pipes stdin through `groff -t -mandoc` and `col -bx` for text formats, or through `groff -Tps` and optionally `ps2pdf` for PDF. Unknown formats exit 1.

## State, Dependencies, and Integration
There is no persistent state; all content streams through stdin/stdout. Dependencies are `groff`, `col`, `sed`, and `ps2pdf` for PDFs. `Makefile.am` uses it in `dist-hook` and `pdf-local`.

## Risks and Test Signals
The script centralizes doc conversion behavior but assumes GNU-ish groff tooling. Errors surface during distribution or PDF targets rather than normal builds.
