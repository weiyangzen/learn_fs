# Group Research: group_1748_spdk_sources_virtualization_spdk_lib_nvme_nvme_opal_c_sources_virtu_eaaeded60ab7

Scope verified against `Docs/research_subset_a.md`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_opal.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_opal.c

## Purpose

Implements SPDK NVMe Opal support for TCG storage security over NVMe Security Send/Receive. It constructs and parses Opal tokens, runs synchronous session-style command flows on the NVMe admin queue, discovers Opal capabilities, and exposes public `spdk_opal_*` commands for ownership, Locking SP activation, locking range setup/status, user/password management, revert, erase, and secure erase.

## Main Responsibilities

- Wrap NVMe Security Send/Receive into `opal_send_recv()`, using async admin commands internally and polling admin completions until a session callback marks completion.
- Serialize Opal commands into a fixed `IO_BUFFER_LENGTH` command buffer with tiny/short/medium atom helpers, byte-string insertion, numeric tokens, and final packet/subpacket length fixups.
- Parse Opal responses into `spdk_opal_resp_parsed`, classifying tiny/short/medium/long atoms and token atoms, then extract method status, unsigned integers, and byte strings.
- Run Discovery0, validate supported security protocols, parse feature descriptors, and populate `spdk_opal_dev` feature/comid state.
- Manage Opal sessions with host/session numbers, authentication UIDs, and TCG methods.
- Implement high-level command workflows: take ownership, construct/destruct device, revert TPer, activate Locking SP, lock/unlock range, setup range, query max ranges/range info, enable/add users, set passwords, erase, and secure erase by regenerating active key.

## Key Control Flow

Construction starts in `spdk_opal_dev_construct()`: allocate device and payload, run `opal_discovery0()`, parse Discovery0 features in `opal_discovery0_end()`, and store the selected comid. Most public commands allocate an `opal_session`, initialize a key with `opal_init_key()`, start either a generic SP session or authenticated Locking SP session, perform one or more command builders, call `opal_send_recv()`, parse method status, then call `opal_end_session()`.

`spdk_opal_cmd_take_ownership()` is a multi-session flow: open Admin SP as Anybody, read MSID PIN, end session, reopen as SID using MSID, then set the SID C_PIN to the new password.

## State and Data

Primary mutable state is `struct spdk_opal_dev` from `nvme_opal_internal.h`: controller pointer, comid, Discovery0 feature info, cached max ranges, and per-locking-range info. Per-command state lives in `struct opal_session`: command/response buffers, parsed response tokens, session IDs, completion callback fields, and synchronous completion status.

## Integration Points

Depends on NVMe controller admin command APIs for security send/receive and completion polling. Uses Opal constants and wire structs from `spdk/opal_spec.h`, public types from `spdk/opal.h`, and SCSI security protocol values from `spdk/scsi_spec.h`.

## Risk Notes

- The parser stores up to `MAX_TOKS` response tokens but does not visibly guard `num_entries` against exceeding that array while parsing malformed large responses.
- `opal_add_token_u64()` writes directly to the command buffer without the same explicit buffer-bound checks used by byte-string helpers.
- Several public wrappers combine operation and end-session return values with `ret += opal_end_session(...)`, which can obscure the original error code.
- Sensitive key material is sometimes zeroed, but not consistently for all stack/session buffers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_opal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_opal_internal.h -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_opal_internal.h

## Purpose

Internal definitions for `nvme_opal.c`. It centralizes Opal buffer sizing, UID/method tables, parsed response token types, session state, and the private `spdk_opal_dev` representation.

## Main Contents

- Constants: `IO_BUFFER_LENGTH` 2048, `MAX_TOKS` 64, `OPAL_KEY_MAX` 256, `OPAL_UID_LENGTH` 8, host session number, invalid-parameter value, and missing-method-status value.
- Atom/token enums: internal token classes for byte strings, signed/unsigned integers, raw Opal tokens, and atom widths.
- UID enum and `spdk_opal_uid` table for SMUID, Admin SP, Locking SP, Anybody, SID, Admin/User authorities, locking ranges, ACEs, C_PIN objects, PSID, and half UIDs.
- Method enum and `spdk_opal_method` table for Properties, StartSession, Revert, Activate, GenKey, Get, Set, Authenticate, Random, Erase, and related methods.
- Internal structs for keys, parsed response tokens, response token arrays, Opal packet header grouping, session state, and device state.

## Integration Points

Included directly by `nvme_opal.c`; also includes `spdk/opal_spec.h`, `spdk/opal.h`, and `spdk/scsi_spec.h`. The UID and method arrays are definitions in the header, so this header is intended for narrow internal inclusion rather than broad reuse.

## Risk Notes

Because the UID/method arrays are non-static definitions in a header, including this header in multiple translation units would create duplicate definitions. Current use appears intentionally local to `nvme_opal.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_opal_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie.c

## Purpose

Implements the PCIe NVMe transport registration and controller-level PCIe behavior: device enumeration, hotplug/remove handling, MMIO register access, BAR/CMB/PMR mapping, controller construction/destruction, admin queue enablement, interrupt enablement, and transport operation table wiring.

## Main Responsibilities

- Register the SPDK PCI NVMe driver and `pcie_ops` transport.
- Handle PCI hotplug add/remove events and explicit physical removal checks.
- Protect MMIO access from SIGBUS on removed devices by tracking the current thread’s MMIO controller and remapping registers to an anonymous page on fault.
- Provide register accessor callbacks for 32-bit and 64-bit NVMe controller registers.
- Map/unmap BAR0, set doorbell base, discover/map CMB and PMR regions, and expose controller memory/persistent memory mapping APIs.
- Enumerate PCI devices, handle primary vs secondary process attach behavior, filter by requested PCI address, and call generic NVMe probe/construct logic.
- Construct PCIe controllers: claim PCI device, allocate `nvme_pcie_ctrlr`, set quirks/NUMA, construct generic controller, map BARs, enable busmaster/disable INTx, compute doorbell stride, construct admin qpair, and add process state.
- Destroy controllers and release admin qpair, generic controller state, BAR mappings, interrupts, PCI claim, and device attachment.

## Key Control Flow

`nvme_pcie_ctrlr_scan()` optionally parses `traddr`, processes hotplug removal events, and calls either full enumeration or direct attach. `pcie_nvme_enum_cb()` formats the PCI BDF into an NVMe transport ID and either attaches secondary processes to existing controllers or probes in the primary process.

`nvme_pcie_ctrlr_construct()` is the main setup path and culminates in `nvme_pcie_ctrlr_construct_admin_qpair()`. `nvme_pcie_ctrlr_enable()` writes ASQ, ACQ, and AQA based on the admin qpair buffers.

## Integration Points

Works with common qpair code in `nvme_pcie_common.c`, structures/inlines from `nvme_pcie_internal.h`, generic controller logic in `nvme_internal.h`, and environment PCI/MMIO/memory registration APIs.

## Risk Notes

- Several construction failure paths after BAR allocation/admin qpair setup rely on generic destructors only in some branches; lifetime ordering is subtle.
- SIGBUS handler uses global/thread-local controller state and remaps MMIO space, so correctness depends on every MMIO access setting/clearing `g_thread_mmio_ctrlr`.
- Secondary processes are explicitly rejected in interrupt mode.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie_common.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie_common.c

## Purpose

Implements the shared PCIe/vfio-user qpair mechanics: queue allocation/reset, admin and I/O qpair create/delete commands, tracker lifecycle, submission/completion processing, PRP/SGL/metadata mapping, poll-group support, and PCIe tracepoint registration.

## Main Responsibilities

- Allocate submission/completion rings, optionally using CMB submission queues, and create tracker arrays sized to avoid CQ wrap issues.
- Maintain PCIe qpair state, queue indices, phase bits, free/outstanding tracker queues, retry counts, and statistics.
- Build and submit NVMe admin commands to create/delete I/O CQs/SQs.
- Handle asynchronous qpair connection state through create-CQ/create-SQ completion callbacks.
- Submit trackers by copying commands into SQ entries, handling fused command doorbell suppression and QEMU maximum access-width quirks.
- Process completions from CQ phase bits, prefetch next tracker, apply architecture barriers, complete or retry requests, ring CQ/SQ doorbells, and run timeout checks.
- Abort outstanding trackers/AERs and manually complete failed requests.
- Delete qpairs, clear shadow doorbells, wait for delete queue admin completions, complete remaining I/O, and free owned resources.
- Build request data pointers using PRP or hardware SGLs for contiguous, callback-SGL, and IOV payloads; map metadata through MPTR or metadata SGL where supported.
- Implement PCIe transport poll group completion processing and stats.

## Key Control Flow

`nvme_pcie_qpair_submit_request()` obtains a free tracker, links it to the request, assigns CID, decides PRP vs SGL based on controller flags/admin queue/opcode quirks, builds payload and metadata mappings, then calls `nvme_pcie_qpair_submit_tracker()`. If mapping fails, completion is deferred through `nvme_pcie_fail_request_bad_vtophys()` so callers see failure via callback rather than synchronous submission failure.

`nvme_pcie_qpair_process_completions()` handles connecting qpairs specially by polling adminq until create commands finish. For normal queues it scans completions by phase, completes trackers, updates stats and doorbells, flushes delayed SQ doorbells, checks timeouts, completes cross-process admin requests, and drains pending vtophys failures.

## Integration Points

Uses `nvme_pcie_internal.h` for transport-private layout and doorbell helpers, generic request/qpair/controller code from `nvme_internal.h`, SPDK env vtophys/memory APIs, trace APIs, and SGL helpers.

## Risk Notes

- The mapping path is dense and assertion-heavy; malformed or unexpected payload type/shape can trip asserts in debug builds.
- Completion handling asserts if a CQE CID does not map to an outstanding tracker, which is appropriate for corruption but fatal.
- Bad vtophys failures are deferred when outside completion context, so tests need to cover delayed failure completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie_common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie_internal.h -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie_internal.h

## Purpose

Private PCIe transport header defining controller/qpair/tracker layouts, queue constants, doorbell helpers, and function prototypes shared by `nvme_pcie.c` and `nvme_pcie_common.c`.

## Main Contents

- Queue sizing constants: min/max completion batch sizes, max SGL descriptors, max PRP list entries, minimum admin queue size.
- `struct nvme_pcie_ctrlr`: embeds generic controller plus MMIO register mapping, CMB state, PMR state, doorbell stride/base, PCI handle, and SIGBUS remap flag.
- `struct nvme_tracker`: one 4 KiB tracker per CID containing request pointer, callback, PRP/SGL bus address, metadata SGL, and union of PRP list or SGL descriptors. Static asserts enforce 4 KiB size and qword alignment.
- `struct nvme_pcie_poll_group`: generic transport poll group plus shared PCIe statistics.
- `struct nvme_pcie_qpair`: hot-path doorbells, SQ/CQ buffers, tracker queues, stats, indices, flags, embedded generic qpair, shadow doorbells, ownership state, bus addresses, and optional user-provided queue memory.
- Inline container conversions for generic-to-PCIe controller/qpair.
- Shadow doorbell event-index logic and SQ/CQ doorbell ringing helpers.
- Prototypes for controller, qpair, tracker, poll-group, and stats functions.

## Integration Points

This header is the contract between transport setup and qpair data path files. It also exposes `g_thread_mmio_ctrlr`, used by MMIO writes and the SIGBUS fault handler in `nvme_pcie.c`.

## Risk Notes

The header encodes layout-sensitive invariants. Changes to `struct nvme_tracker` can break the 4 KiB PRP boundary guarantee, while moving qpair fields can affect hot-path cache locality and doorbell correctness.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_pcie_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_poll_group.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_poll_group.c

## Purpose

Implements the public NVMe poll-group abstraction over transport-specific poll groups. It groups qpairs by transport, optionally integrates interrupt/eventfd handling, validates accelerator callback tables, dispatches completion polling/waiting, and aggregates per-transport stats.

## Main Responsibilities

- Create/destroy `spdk_nvme_poll_group`, initialize optional accel function table, fd group, disconnect eventfd, context, and transport-group list.
- Validate that acceleration sequence callbacks are all present or all absent, and that append callbacks have required sequence callbacks.
- Add/remove qpairs by finding or creating the matching transport poll group.
- Enforce that all qpairs in one poll group use the same interrupt mode.
- In Linux interrupt mode, create a disconnect eventfd, add qpair fds to the fd group, and invoke the configured interrupt callback when events arrive.
- Connect/disconnect qpairs through transport callbacks while adding/removing qpair fd handlers.
- Process completions across transport groups with recursion protection.
- Wait for fd-group events after checking disconnected qpairs.
- Report whether all qpairs are connected, preserving disconnected qpair priority over still-connecting state.
- Aggregate and free per-transport poll-group statistics.

## Key Control Flow

`spdk_nvme_poll_group_add()` requires qpairs to be disconnected, initializes interrupt-mode consistency on first add, lazily creates a transport-specific poll group, and delegates add to the transport. `spdk_nvme_poll_group_process_completions()` iterates all transport groups and returns the first negative transport error if any, otherwise total completions.

## Integration Points

Calls transport abstraction functions from `nvme_internal.h`, qpair state helpers, fd group APIs, Linux `eventfd`, and the PCIe/fabrics transport poll-group implementations.

## Risk Notes

- Destroy returns `-EBUSY` if any transport poll group cannot be destroyed, preserving the group list for retry.
- Interrupt fd handling has Linux-specific behavior; non-Linux builds stub disconnect fd support with `-ENOTSUP`.
- `spdk_nvme_poll_group_wait()` assumes fd group support exists and a non-null disconnected-qpair callback is supplied.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_poll_group.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_qpair.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_qpair.c

## Purpose

Implements generic NVMe qpair behavior above individual transports: command/completion formatting, status string lookup, retry classification, queued request abort/resubmission, completion processing wrapper, qpair initialization/deinitialization, submission state machine, error injection, and public qpair accessors.

## Main Responsibilities

- Convert admin, fabrics, I/O, feature, SGL, and completion status values to diagnostic strings.
- Print commands and completions, including opcode-aware fabric command status via newer `_ext` APIs.
- Define qpair state names and retry policy for selected generic/path status codes.
- Manually complete requests for abort/error paths and abort queued requests with or without matching callback arg.
- Handle qpair enable transitions after connect/reset, including PCIe-specific abort of old queued/outstanding requests during reset.
- Process completions through transport callbacks while handling admin register completions, transport events, failed controllers, error injection, completion-context deletion, and queued request resubmission.
- Initialize qpair request pools, including a reserved request, free/queued/aborting/error queues, transport type, state fields, and async flag.
- Deinitialize by aborting queued/error requests and freeing request/error command allocations.
- Submit requests through `_nvme_qpair_submit_request()`, including split parent/child handling, queued request preservation, fabrics connect exceptions, reset queuing, and error cleanup.
- Add/remove command error injection entries.

## Key Control Flow

`spdk_nvme_qpair_process_completions()` is the generic completion entry point. It handles admin-only register and transport events, checks controller/qpair state, completes injected errors, calls the transport completion function inside completion context, handles deferred qpair deletion, then resubmits as many queued requests as completions processed.

`nvme_qpair_submit_request()` sets timeout state, preserves FIFO ordering if queued requests already exist, calls `_nvme_qpair_submit_request()`, and queues on `-EAGAIN`.

## Integration Points

Depends on transport ops, controller state/locking helpers, request allocation/completion helpers, SPDK logging/deprecation, OCSSD opcodes, and public qpair APIs.

## Risk Notes

- Submission, reset, and reconnect paths are state-machine-sensitive, especially around PCIe reset exceptions and split requests.
- Error injection changes normal request flow and requires cleanup in qpair deinit.
- Completion callbacks may submit or abort more requests, so abort paths deliberately avoid recursive completion loops.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_qpair.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_quirks.c -->
# File Research: sources/virtualization/spdk/lib/nvme/nvme_quirks.c

## Purpose

Maps PCI IDs to SPDK NVMe controller quirk flags. This lets PCIe controller construction adapt behavior for known devices, vendors, and virtual controllers.

## Main Responsibilities

- Define `struct nvme_quirk` entries keyed by `spdk_pci_id`.
- Match Intel, Memblaze, Samsung, VirtualBox, Red Hat, CNEX Labs, VMware, Huawei, Microsoft, and Micron IDs to flags such as latency log quirks, striping, read-zero-after-deallocate, initialization delays, minimum queue sizes, no SGL for DSM, maximum PCI access width, OCSSD, security OACS, MDTS metadata handling, not using SGL, and MSI-X vector count behavior.
- Implement wildcard-aware PCI ID matching where fields in the quirk entry may be `SPDK_PCI_ANY_ID` or class-any.
- Return matching flags from `nvme_get_quirks()` and debug-log each enabled quirk.

## Integration Points

Called by PCIe controller construction in `nvme_pcie.c` after reading `spdk_pci_id` from the PCI device. Flags are consumed across controller setup and qpair submission paths, including CMB command copy width and SGL selection.

## Risk Notes

The table returns the first matching entry. Broad wildcard entries must remain ordered after more specific entries for the same vendor/class to avoid masking device-specific behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvme/nvme_quirks.c -->