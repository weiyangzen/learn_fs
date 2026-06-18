# sources/distributed-fs/ceph-client/fs/btrfs/send.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/send.h` declares the Btrfs send stream wire-format constants and the `btrfs_ioctl_send()` prototype used by the Btrfs ioctl layer. It defines stream magic/version selection, command-buffer size rules, packed stream/TLV header structures, command IDs, attribute IDs, and protocol-version maxima. The source was read as a complete 187-line file for this report.

## Important APIs, Types, and Functions

The only function prototype is `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`, implemented in `send.c`.

Important constants are `BTRFS_SEND_STREAM_MAGIC`, `BTRFS_SEND_STREAM_VERSION`, `BTRFS_SEND_BUF_SIZE_V1`, and `BTRFS_SEND_BUF_SIZE_V2`. `BTRFS_SEND_STREAM_VERSION` is `3` only under `CONFIG_BTRFS_EXPERIMENTAL`; otherwise it is `2`. v1 commands are bounded by a 64 KiB command buffer, while v2 uses an aligned buffer sized for a command header plus compressed extent data.

Packed wire-format structures are `struct btrfs_stream_header` (`magic`, little-endian `version`), `struct btrfs_cmd_header` (`len`, `cmd`, `crc`), and `struct btrfs_tlv_header` (`tlv_type`, `tlv_len`). They are declared packed because their exact byte layout is part of the send-stream ABI.

`enum btrfs_tlv_type` defines local type categories for TLV interpretation: integer widths, binary, string, UUID, and timespec. `enum btrfs_send_cmd` assigns stable numeric command IDs. v1 includes subvolume/snapshot, create, rename/link/unlink/rmdir, xattr, write/clone, truncate/chmod/chown/utimes/end/update-extent. v2 adds fallocate, fileattr, and encoded write. v3 adds enable-verity. The anonymous attribute enum assigns stable IDs for UUIDs, ctransids, inode metadata, xattrs, paths, write data, clone metadata, fallocate mode, file attributes, encoded-write metadata, compression/encryption, and fs-verity descriptor fields.

## Control Flow

This header has no executable control flow. It controls compile-time and ABI flow by constraining which command and attribute IDs are valid for each protocol version. `send.c` uses the version maxima in `proto_cmd_ok()`, uses buffer-size macros while allocating `send_ctx.send_buf`, emits `btrfs_stream_header` through `send_header()`, emits `btrfs_cmd_header` through `begin_cmd()`/`send_cmd()`, and emits `btrfs_tlv_header` through `tlv_put()` and v1 data headers.

The protocol-version boundary also affects runtime feature selection: v1 streams cannot emit fallocate, fileattr, encoded write, or verity commands; v2 can emit encoded compressed data and fallocate hole punching; v3 can emit `BTRFS_SEND_C_ENABLE_VERITY` when experimental support is built.

## State and Persistence Behavior

The file owns no runtime storage. Its packed structures and numeric enums define the persistent byte format written into send streams and later consumed by receivers. Changing command IDs, attribute IDs, field sizes, packing, endianness, or version maxima changes the on-disk/on-pipe ABI for send streams.

`BTRFS_SEND_A_DATA` has special persistence semantics starting with protocol v2: the header includes only the attribute type and the data length is implied by the remaining command length. This is why `send.c` must place DATA last and prevent further TLVs after it.

## Dependencies and Integration Points

The header includes `<linux/types.h>`, `<linux/sizes.h>`, and `<linux/align.h>`, and depends on `BTRFS_MAX_COMPRESSED` and `PAGE_SIZE` being available through the wider Btrfs/kernel include context. It forward declares `struct btrfs_root` and `struct btrfs_ioctl_send_args` to avoid pulling in heavier Btrfs internals.

The primary integration points are the kernel send implementation in `send.c`, the ioctl declarations that define `btrfs_ioctl_send_args` and send flags, and userspace/kernel receive implementations that parse this exact stream format. The command and attribute enums are a cross-version compatibility contract between senders and receivers.

## Risks and Edge Cases

The command and attribute numbers are ABI-stable; reordering or renumbering would break all existing receivers. Adding a new command requires updating version-specific maxima and ensuring `send.c` gates emission through protocol checks. Adding attributes requires receiver compatibility rules, especially if the attribute is mandatory for interpreting command payloads.

Packed structure layout and little-endian fields are critical. Any compiler/layout drift or accidental padding would corrupt stream parsing. The v2 `BTRFS_SEND_A_DATA` exception is easy to mishandle because it does not use the ordinary `struct btrfs_tlv_header` length field.

Buffer-size macros are tied to protocol behavior. v1 assumes no command is larger than 64 KiB. v2 must be large enough for a header plus compressed extent data and page-aligned vmalloc/page mapping used by encoded reads. If `BTRFS_MAX_COMPRESSED` or compression behavior changes, send buffer assumptions need review.

`CONFIG_BTRFS_EXPERIMENTAL` changes the advertised maximum stream version. Builds without it must not emit v3 fs-verity commands even if the code paths compile, and userspace requesting a higher version should be rejected.

## Test Signals

Compile tests should cover builds with and without `CONFIG_BTRFS_EXPERIMENTAL` so `BTRFS_SEND_STREAM_VERSION` and v3 maxima are correct. ABI tests should assert packed structure sizes and command/attribute numeric values. Stream round-trip tests should parse v1 and v2 streams, including v2 DATA attributes without explicit lengths. Feature tests should request unsupported versions and verify `btrfs_ioctl_send()` rejects them, and should verify that fallocate/fileattr/encoded-write/verity commands only appear in compatible stream versions.
