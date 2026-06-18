# sources/distributed-fs/ceph-client/drivers/video/logo/pnmtologo.c

Purpose: host build utility that converts ASCII PNM logo images into C source containing `struct linux_logo` data arrays suitable for kernel inclusion.

Important APIs, types, and functions: global options are `-t` type, `-n` logo name, `-o` output, and input filename. Main helpers are `get_number`, `get_number255`, `read_image`, validation helpers, `write_header`, `write_footer`, `write_hex`, `write_logo_mono`, `write_logo_vga16`, `write_logo_clut224`, `write_logo_gray256`, `die`, `usage`, and `main`.

Control flow: `main` parses options, reads an ASCII PBM/PGM/PPM image, and dispatches to the selected output writer. `read_image` rejects binary PNM, parses width/height/maxval, allocates `logo_data`, and normalizes channels to 0..255. Output writers validate constraints: mono must be black/white, VGA16 must match the fixed VGA palette, CLUT224 builds a palette up to 224 colors and encodes indexes offset by 32, and gray256 requires equal RGB channels. The generated file includes logo data, optional CLUT, and a `const struct linux_logo`.

State and persistence: process-local heap state for image rows and palette, output file or stdout, and generated C source on disk. No runtime kernel state.

Dependencies and integration points: built as a Kbuild host program from `logo/Makefile`; output consumed by logo object builds and `logo.c`.

Risks: binary PNM files are unsupported and require pre-conversion. Parsing uses simple heap allocations and exits on fatal errors; no cleanup is needed for a short-lived host tool but malformed huge dimensions can demand large memory. PBM parsing includes a workaround for some non-spaced exports. CLUT order follows first occurrence, so image changes alter generated data layout.

Test signals: run converter on valid mono, VGA16, CLUT224, and gray256 ASCII images; test invalid binary PNM, too many colors, out-of-palette VGA16, non-gray gray256, comments/whitespace parsing, custom symbol name, stdout and `-o` paths.
