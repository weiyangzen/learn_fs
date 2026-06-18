# Chunk Research: sources/virtualization/nvme-cli/nvme.c lines 1-9504

## Scope

This chunk covers the beginning through most of the generic passthrough implementation of `nvme.c`. It defines the built-in `nvme` CLI program object, common option/config structures, shared open/parse helpers, and a large set of built-in command handlers for identify, logs, namespace management, firmware, controller registers/properties, format/sanitize, feature get/set, security/directive commands, core I/O commands, reservations, and the start of arbitrary admin/I/O passthrough.

The chunk ends at line 9504 inside `passthru()`, immediately after data-buffer allocation/prefill and before the rest of passthrough command construction/execution. The file tail after this range contains cross-chunk continuations for passthrough wrappers, NVMe-oF host/key/TLS commands, fabrics connect/discover commands, NVMe-MI helpers, additional log readers, extension registration, and `main()`.

## Program and Shared State

- Built-in command registration is created via `CREATE_CMD` plus `nvme-builtin.h`, then wrapped in `builtin` and `nvme`.
- Shared CLI state lives in `struct nvme_args nvme_args`, including output format, timeout, verbosity, dry-run, and ioctl-probing behavior.
- Main reusable config structs in this range: `feat_cfg`, `passthru_config`, `get_reg_config`, and `set_reg_config`.
- Most command handlers use cleanup attributes for libnvme allocations, global contexts, transport handles, file descriptors, and huge allocations.

## Control Flow and APIs

- `parse_and_open()` is the standard command prologue: parse options, create libnvme context, configure ioctl probing, open the transport handle, install submit/retry hooks, apply dry-run and timeout.
- `open_fallback_chardev()` reopens controller handles as `/dev/<ctrl>n<nsid>` for namespace I/O commands.
- `validate_output_format()` maps `normal`, optional `json`, `binary`, and `tabular` to print flags.
- The command body pattern is usually: parse/open, validate output, derive namespace/controller state, allocate buffers, initialize command, execute through libnvme, print via `nvme_show_*`.

## Command Families

- Log commands cover SMART, ANA, telemetry, endurance, command effects, supported logs, error, firmware, changed namespace lists, predictable latency, persistent event, LBA status, reservation notification, boot partition, PHY RX EOM, media unit, capacity config, sanitize, FID effects, and MI command effects.
- Identify/list commands cover controllers, namespaces, command sets, UUIDs, NVM sets, domains, primary/secondary controller virtualization capabilities, topology list, subsystem list, and `top`.
- Namespace management includes create/delete/attach/detach, with `create_ns()` deriving FLBAS, namespace granularity, SI sizes, ZNS fields, placement handles, and issuing namespace management passthrough.
- Firmware and destructive maintenance include firmware download/commit, reset/subsystem reset/rescan, sanitize, sanitize namespace, and format.
- Register/property handling chooses MMIO mapping when possible and falls back to NVMe fabrics Get/Set Property.
- Feature handling supports feature iteration, changed/default comparison, feature payload buffers, timestamp convenience encoding, and set-feature payload reads.
- I/O paths include write zeroes, write uncorrectable, DSM, copy, flush, reservations, read/write/compare through `submit_io()`, verify, security send/receive, directives, lockdown, and RPMB handoff.
- Generic passthrough starts at the end of the chunk, parsing opcode/CDWs/data/metadata/read/write/raw/show/latency options and allocating buffers before the chunk boundary.

## Dependencies

- Heavy dependence on libnvme transport handles, topology scanning, identify/log/feature helpers, raw admin and I/O passthrough, status helpers, huge memory allocation, resets, namespace operations, fabrics properties, and optional NVMe-MI endpoints.
- Local dependencies include `util/argconfig.h`, `nvme-cmds.h`, `nvme-print.h`, `logging.h`, `util/suffix.h`, `util/sighdl.h`, `util/cleanup.h`, and `malloc.h`.
- Platform dependencies include Linux NVMe device nodes, `/sys/class/nvme/.../resource0`, POSIX file I/O, `mmap`, `fsync`, `fstat`, and compile-time `CONFIG_JSONC`, `CONFIG_MI`, `NVME_HAVE_MMAP`.

## Risks and Edge Cases

- `get_transport_handle()` accepts `flags` but does not use them, so `open_exclusive()` appears not to enforce `O_EXCL` in this visible path.
- `is_ns_mgmt_support()` appears inverted: it returns false on successful allocation and would identify through a null pointer if allocation failed.
- `get_feature_id()` allocates `data_len - 1` but passes `data_len` to `nvme_get_features()`.
- `get_feature_id_changed()` uses `strcmp()` on binary buffers and appears to print when current/default buffers are equal.
- `sec_send()` can read more bytes than the allocated transfer buffer when the file is larger than `--tl`.
- `submit_io()` returns the current `err` for invalid `prinfo > 0xf`, often meaning success.
- Some file-output paths do not robustly handle short writes.
- Several user-controlled lengths allocate large buffers directly.
- Destructive commands rely on mixed validation, prompts, and intended exclusivity; automation should treat format/sanitize/write/register/namespace/firmware paths as hardware state-changing.

## Cross-Chunk References

- `passthru()` continues after line 9504 and must be completed by the next chunk.
- Later chunks implement `io_passthru()`, `admin_passthru()`, host NQN/key/TLS commands, fabrics discover/connect/disconnect/config/DIM, NVMe-MI helpers, late log commands, `register_extension()`, and `main()`.
- Helpers defined here are used later: `nvme_args`, `validate_output_format()`, `parse_and_open()`, `open_exclusive()`, `put_transport_handle()`, `get_reg_size()`, `nvme_is_ctrl_reg()`, and `elapsed_utime()`.