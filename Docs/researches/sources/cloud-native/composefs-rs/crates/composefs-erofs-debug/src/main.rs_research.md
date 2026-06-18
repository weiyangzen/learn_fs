# sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/src/main.rs

Purpose: command-line utility that dumps an entire EROFS image in a detailed, deterministic, diff-friendly format for inspection and comparison.

Important APIs/types/functions: `Args` derives `clap::Parser` and carries one `PathBuf` field, `image`. `main` opens the path, reads the whole file into a `Vec<u8>`, and calls `composefs::erofs::debug::debug_img(&mut stdout, &data)`.

Control flow: parse CLI arguments, open the image, read it fully, then stream the debug renderer to stdout. Failures use `expect` for file open/read and `unwrap` for debug rendering, making this a diagnostic tool rather than a polished user-facing CLI.

State and persistence: it only reads the image and writes stdout. It does not mutate the repository or image.

Dependencies and integration points: depends on `clap` for argument parsing and `composefs::erofs::debug::debug_img` for all domain-specific parsing/rendering. The deterministic output is useful alongside image determinism tests and EROFS writer comparisons.

Risks: reads the whole image into memory, so very large images can be expensive. Panic-style errors are acceptable for debugging but poor for automation expecting structured failures. Correctness is entirely delegated to the `debug_img` parser.

Test signals: no tests are local to this file. Existing mkcomposefs determinism tests and any manual byte-diff investigations are the main consumers of the behavior.
