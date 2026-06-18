# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h lines 1-3335

## Scope

This chunk covers the opening of the LP10000 Emulex firmware header and the first 3,310 data rows of `emlxs_lp10000_image[]`. The C source range starts with the file license/header guard at line 1 and ends in the middle of the byte array at line 3335, at image offset `0x06768`. Each image row contains 8 bytes, so this chunk contributes bytes `0x00000` through `0x0676F` inclusive, or `0x6770` / 26,480 bytes, of the firmware image.

## APIs And Exposed Contract

- Header guard: `_FW_LP10000_H` protects this firmware-specific header from repeated inclusion.
- C++ compatibility wrapper: `extern "C"` is opened when `__cplusplus` is defined. The matching close is outside this chunk.
- Firmware identity macros are exported unconditionally:
  - `emlxs_lp10000_label`: `"LP10000-S: v1.92a1 (td192a1.all)"`
  - `emlxs_lp10000_kern`: `0xFF801416`
  - `emlxs_lp10000_stub`: `0x02881991`
  - `emlxs_lp10000_sli1`: `0x06831991`
  - `emlxs_lp10000_sli2`: `0x07831991`
  - `emlxs_lp10000_sli3`: `0x00000000`
  - `emlxs_lp10000_sli4`: `0x00000000`
- `EMLXS_FW_IMAGE_DEF` gates the actual image definition. When it is defined, this chunk starts an 8-byte-aligned `static uint8_t emlxs_lp10000_image[]` initializer. When it is not defined, only metadata macros are available in this chunk; the fallback `emlxs_lp10000_image`/`emlxs_lp10000_size` zero macros are later in the file, outside this chunk.
- The adjacent firmware table header `emlxs_fw.h` consumes these symbols in the `LP10000_FW` entry of `EMLXS_FW_TABLE`, mapping size, image pointer, label, kernel/stub revision, and SLI revision fields into `emlxs_firmware_t`.

## Data And Firmware Layout Visible Here

- The image payload is emitted as a C byte array with offset comments and printable ASCII comments. The chunk is not normal driver source code; it is mostly an opaque firmware binary embedded in a header.
- The first bytes look like ARM instruction encodings (`0xE1A00000`, `0xE1A01001`, `0xE59FF3F8`, `0xEA...`), with vector/branch-table-like regions near offsets `0x00080` and `0x00180`.
- Early metadata-like words are visible in big-endian byte order:
  - offset `0x00038`: `FF 80 14 16`, matching `emlxs_lp10000_kern`.
  - offset `0x00268`: sentinel-looking `12 34 56 78`.
  - offset `0x00270`: `FF 80 14 16`, again matching the kernel revision.
- The chunk includes long zero-filled regions early in the image, then denser instruction/literal data. In this line range, 465 image rows are all zero bytes and 2,845 contain nonzero data.
- Around offsets `0x06180` through `0x06768`, the payload visibly contains code patterns consistent with formatted output/parsing helpers: checks for ASCII characters such as `%`, `+`, space, `#`, `-`, `0`, `.`, `l/L`, `h`, `g`, `c`, `d`, `e/f`, `p`, `i`, `n`, `o`, `s`, `u`, and `x`, plus embedded digit tables `0123456789ABCDEF` and `0123456789abcdef`, and prefixes `0X`/`0x`.

## Control Flow

- At the C/preprocessor level, control flow is limited to include guards and conditional image materialization:
  - Always define the LP10000 revision/label macros.
  - Only allocate and initialize `emlxs_lp10000_image[]` when `EMLXS_FW_IMAGE_DEF` is defined.
- At the firmware payload level, the binary contains branch and call encodings. Because the source is emitted as raw bytes, semantic control flow cannot be proven from C symbols in this chunk. The visible patterns suggest an embedded ARM firmware entry/vector area at the beginning and runtime helper routines later in the chunk, but the host driver treats this data as a loadable image rather than executing it on the host CPU.

## State And Mutability

- The only host-side storage introduced in this chunk is `static uint8_t emlxs_lp10000_image[]` under `EMLXS_FW_IMAGE_DEF`.
- The array is `static`, so each translation unit that defines `EMLXS_FW_IMAGE_DEF` and includes this header gets its own internal-linkage copy. The intended pattern in `emlxs_fw.h` is to define the image in the firmware table module, not broadly in arbitrary files.
- The array is not declared `const`; host-side code could mutate it if it has access to the symbol in the same translation unit. No mutation occurs in this chunk.
- Firmware state, MMIO state, mailbox state, and download progress are not represented as C variables here. They are encoded inside the opaque image or handled by other `emlxs` driver modules.

## Dependencies

- Requires `uint8_t` to be visible before inclusion when `EMLXS_FW_IMAGE_DEF` is enabled.
- Uses an illumos/Sun-style `#pragma align 8(emlxs_lp10000_image)` to force image alignment.
- Depends on `EMLXS_FW_IMAGE_DEF` policy from the including firmware-table build. In adjacent context, `emlxs_fw.h` defines `EMLXS_FW_IMAGE_DEF` only when building a compiled-in firmware table without `MODFW_SUPPORT`.
- Depends on `emlxs_firmware_t` consumers using the revision macros consistently. `emlxs_fw.h` defines fields for `kern`, `stub`, `sli1`, `sli2`, `sli3`, and `sli4`; this LP10000 image advertises SLI1 and SLI2 firmware revisions and zeroes SLI3/SLI4.

## Risks And Review Notes

- Opaque binary blob: source review cannot validate firmware behavior, bounds checks, or device-side trust properties from this C representation alone.
- Header-defined storage: accidental inclusion with `EMLXS_FW_IMAGE_DEF` in more than one translation unit duplicates a large static image and can diverge from the intended firmware table layout.
- Non-`const` payload: the image is mutable in C even though it is logically firmware data.
- Version coupling: the metadata macros and embedded bytes both encode revision-like values. Any manual edit must keep header macros, image metadata, and firmware table expectations aligned.
- Hardware compatibility risk is explicit: SLI3 and SLI4 revisions are zero for LP10000, so consumers should not treat this image as supporting those interfaces.
- Portability/build risk: `#pragma align` and the huge static initializer are compiler/build-environment specific and are meant for the illumos kernel build, not a generic userspace compiler.
- Licensing: the file carries an Emulex license notice referring to `License 2 of LICENSE.txt`, not the CDDL header used by adjacent driver headers.

## Cross-Chunk References

- This chunk leaves `emlxs_lp10000_image[]` open. Later chunks continue the byte initializer from offset `0x06770` through the end of the firmware image.
- Adjacent end-of-file context shows the image eventually closes as `emlxs_lp10000_image[] (0x5BD00 bytes)` and defines `emlxs_lp10000_size` as `sizeof (emlxs_lp10000_image)` when `EMLXS_FW_IMAGE_DEF` is active.
- The not-`EMLXS_FW_IMAGE_DEF` branch later in the same file defines `emlxs_lp10000_image` and `emlxs_lp10000_size` as zero values, allowing metadata-only inclusion without embedding the image.
- `emlxs_fw.h` is the main visible consumer: it includes `fw_lp10000.h` and places these macros/symbols into the `LP10000_FW` descriptor in `EMLXS_FW_TABLE`.