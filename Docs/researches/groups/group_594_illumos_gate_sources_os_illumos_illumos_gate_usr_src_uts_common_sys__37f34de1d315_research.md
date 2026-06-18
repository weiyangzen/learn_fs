# Group Research: group_594_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__37f34de1d315

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all seventeen requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsit_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsit_common.h

## Role

`iscsit_common.h` defines the shared user/kernel configuration ABI for the illumos COMSTAR iSCSI target provider. It names the iscsit pseudo-device, ioctl commands, SMF/administration status values, nvlist property names, authentication mode strings, configuration object layouts, and conversion/free helpers used by management tools and the kernel driver.

## Major Definitions

The file defines API version `ISCSIT_API_VERS0`, the module/device names, service ioctl numbers, and `iscsit_hostinfo_t`, which carries a fully qualified host name for iSNS entity identifiers during service enable. `iscsit_ioc_set_config_t` and `iscsit_ioc_getstate_t` pass packed nvlists across the ioctl boundary, with `_SYSCALL32` variants using `caddr32_t` for 32-bit callers.

The configuration model is a linked-object graph:
- `it_tpgt_t` binds a target portal group name to an RFC 3720 target portal group tag and carries a generation counter.
- `it_tgt_t` represents an iSCSI target node, its TPGT list, and target nvlist properties such as target CHAP credentials, alias, and auth policy.
- `it_portal_t` stores a `sockaddr_storage` endpoint and links portal lists.
- `it_tpg_t` represents a named target portal group and its portal list.
- `it_ini_t` represents an initiator context and its CHAP properties.
- `it_config_t` aggregates the persistent STMF token, targets, TPGs, initiators, iSNS server portals, counts, and global properties.

The property macros define the string keys stored in nvlists: global and target auth/alias fields, CHAP credentials, RADIUS server/secret, iSNS enable/server settings, and target rename support.

## Interfaces

The header declares bidirectional conversion routines between C structures and nvlists for configs, target lists, targets, TPG tags, TPGs, initiators, and lists of each object type. It also declares lookup helpers for targets, TPGs, portals, and iSNS servers; sockaddr comparison and string conversion helpers; address-string parsing; array-to-portal-list conversion; recursive free helpers for each object family; and base64 encode/decode helpers for iSCSI secrets.

## Integration Notes

This is an ABI-sensitive header shared by userland administration code and the kernel. Structure sizes, ioctl values, property key strings, list ownership, and generation counters must remain compatible with existing management tools and the driver. Address parsing and nvlist conversion are central trust boundaries because malformed portal strings, packed nvlists, and credential fields cross between userland, persistent STMF provider data, and kernel state.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsit_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/isns_protocol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/isns_protocol.h

## Role

`isns_protocol.h` defines the wire-format constants and lightweight packet structures for iSNS traffic used by the iSCSI target service. It captures iSNS versioning, PDU sizing, function IDs, flags, response codes, attribute IDs, bitmaps, default IDs, name limits, and TLV/PDU structures.

## Major Definitions

The file sets protocol version `0x01`, default server port `3205`, a 12-byte PDU header, 4-byte response code, maximum payload size `65532`, and maximum PDU size as header plus payload. It defines iSNS function IDs for device attribute registration/query/get-next/deregister, SCN, discovery-domain and discovery-domain-set operations, ESI, heartbeat, and response forms.

Flag definitions cover first/last PDU, replace-registration, authentication block, server, and client flags. Response status constants cover success and protocol/server errors such as malformed messages, invalid registration/query/deregistration, unauthorized source, unsupported version/message, busy state, and unavailable ESI.

Attribute ID macros cover entity, portal, iSCSI node, portal group, discovery domain set, discovery domain, and DD feature attributes from iSNS drafts/RFC 4171. Additional masks define entity protocols, protocol version range packing, portal port/type bits, portal security bitmap bits, iSCSI node type bits, SCN bitmap bits, portal group tag bits, DDS status, DD bootlist, default PGT/DD IDs, and maximum/minimum name lengths.

The structures model variable-length packet data: `isns_tlv_t` is a TLV header with flexible first byte, `isns_packet_data_t` stores parsed header fields and an inline TLV array, `isns_reg_mesg_t` groups source/message/delimiter/operating attributes, `isns_resp_mesg_t` groups response status plus attributes, `isns_pdu_t` is the raw PDU header plus payload, and `isns_resp_t` is a response status plus data.

## Interfaces

There are no function prototypes. Consumers use these constants and structures to compose, parse, validate, and interpret iSNS PDUs.

## Integration Notes

This header is tightly coupled to network byte order handling and bounds checks in the implementation. The structures use one-byte trailing arrays for variable payloads, so callers must allocate and validate actual buffer sizes using the defined header, response, TLV, payload, and PDU size constants.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/isns_protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_packet.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_packet.h

## Role

`radius_packet.h` defines the kernel-side packet description and send/receive entry points for iSCSI target RADIUS authentication. It builds on `radius_protocol.h` and represents decoded request/response attributes around illumos kernel sockets.

## Major Definitions

The file defines receive timing policy: `RAD_RCV_TIMEOUT` is five seconds per receive attempt and `RAD_RETRY_MAX` is two retries. `radius_attr_t` stores an attribute type code, value length, and a fixed maximum RADIUS attribute value buffer. `radius_packet_data_t` stores the RADIUS code, identifier, request/response authenticator, an attribute count, and a fixed four-element attribute array. The comment notes current outbound requests need only three attributes.

Response receive status values distinguish success, no data, timeout, protocol error, and authentication failure.

## Interfaces

`iscsit_snd_radius_request()` sends a request on a kernel socket to a RADIUS server IP/port using a populated packet descriptor and returns positive on success. `iscsit_rcv_radius_response()` receives and authenticates a response using the shared secret and original request authenticator, returning one of the local receive status codes and filling a packet descriptor.

## Integration Notes

This interface is part of the iSCSI target authentication path. Callers must enforce attribute count limits, shared-secret length constraints from `radius_protocol.h`, and authenticator validation; the fixed attribute array makes overflow checks straightforward but also constrains future RADIUS attribute expansion.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_packet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_protocol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_protocol.h

## Role

`radius_protocol.h` defines the RADIUS RFC 2865 constants and raw packet shape needed by the iSCSI target RADIUS client code.

## Major Definitions

Packet code constants cover Access-Request, Access-Accept, and Access-Reject. Attribute constants cover User-Name, CHAP-Password, and CHAP-Challenge. The file defines the one-octet identifier length, 16-byte CHAP password string, 16-byte authenticator, maximum 253-byte attribute value, minimum 20-byte packet length, maximum 4096-byte packet length, and local shared-secret bounds of 16 to 128 bytes.

`radius_packet_t` models the raw wire packet: code, identifier, two-byte length, 16-byte authenticator, and variable data. `RAD_PACKET_HDR_LEN` is the fixed 20-byte header size.

## Interfaces

There are no function prototypes. Packet send/receive code includes this header to interpret packet bytes and validate field lengths.

## Integration Notes

The raw length field is byte-array based rather than a host-endian integer, which makes endian handling explicit in implementation code. The shared-secret maximum is a local policy even though the protocol has no defined upper bound.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/radius_protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iso/signal_iso.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iso/signal_iso.h

## Role

`signal_iso.h` provides the ISO C/POSIX-visible signal-number and signal-handler macro subset included indirectly through public Sun/illumos signal headers. It is intentionally limited to standard identifiers and compatibility aliases.

## Major Definitions

The file defines traditional UNIX signal numbers from `SIGHUP` through `SIGINFO`, including aliases such as `SIGABRT`/`SIGIOT`, `SIGCHLD`/`SIGCLD`, and `SIGIO`/`SIGPOLL`. It reserves real-time signal bounds as `_SIGRTMIN` 42 and `_SIGRTMAX` 73, while public `SIGRTMIN` and `SIGRTMAX` are computed dynamically through private `_sysconf(_SC_SIGRT_MIN/MAX)`.

Signal action macros are C++-, lint-, and C-specific forms of `SIG_DFL`, `SIG_ERR`, `SIG_IGN`, and `SIG_HOLD`. For C++, the file introduces `SIG_FUNC_TYP`, `SIG_TYP`, and `SIG_PF` to type signal handlers. It also defines `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK` values for signal-mask operations.

## Interfaces

The only function declaration is private `_sysconf(int)`, used by the real-time signal macros. The rest of the file is macro/type definition.

## Integration Notes

This header is a public ABI surface. Signal numbers and handler sentinel values are not ordinary internal constants; changing them would break applications, libc behavior, and kernel/user signal semantics. New standard signal identifiers are expected to be added here and coordinated with `<sys/signal.h>` namespace handling.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iso/signal_iso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/jioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/jioctl.h

## Role

`jioctl.h` preserves low-level ioctl and packet constants for communication with historical windowing terminals and the `xt` driver. It documents the Jerq/Blit/5620/615/620/630 lineage and defines host-to-terminal and terminal-to-host control message layouts.

## Major Definitions

The `JTYPE` ioctl namespace is `('j' << 8)`. Defined requests include booting a window download, returning to default terminal emulation, querying layers, querying window size, setting millisecond timeouts, booting with debugger wait, bidirectional agent control, running layers, and setting xt protocol type.

`struct jwinsize` reports window dimensions in characters and pixels. `struct jerqmesg` carries a control command and channel. Terminal-to-host control codes describe data delivery, layer creation/deletion/reshape, unblock/exit/defunct/run events, and flow-control toggles. `struct bagent` carries source/destination byte-string pointers plus size for `JAGENT`.

## Interfaces

There are no function prototypes. The header exports ioctl numbers and control packet layouts used by terminal/xt consumers.

## Integration Notes

This is compatibility infrastructure for old terminal protocols. The pointer-bearing `struct bagent` is ABI-sensitive and architecture-sensitive; any ioctl handler must account for user/kernel pointer copying and possible 32-bit compatibility if still reachable.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/jioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbd.h

## Role

`kbd.h` defines Sun/PC/USB keyboard type constants, keyboard event codes, translation modes, modifier-state masks, keyboard table structures, compose/floating-accent structures, and encoded keymap action values used by the keyboard translation layer.

## Major Definitions

The header keeps obsolete keyboard type and command macros for source compatibility while identifying supported keyboard types: Sun Type 3, Sun Type 4, USB, PC 101, and ASCII-terminal keyboard. It defines special device bytes such as idle, error, reset, layout-prefix, pressed, and released, plus Sun keyboard control commands for reset, bell, click, autotest, LED setting, and layout query.

Translation modes are `TR_NONE`, `TR_ASCII`, `TR_EVENT`, and `TR_UNTRANS_EVENT`. `BUILDKEY`, `STATEOF`, and `KEYOF` encode/decode raw key transitions. Modifier and "bucky" state definitions cover Meta/System, caps/shift/control masks, AltGraph, Alt, NumLock, right Alt, and the reserved `UPMASK`.

The keymap model uses `keymap_entry_t` and either fixed-size `struct keymap` arrays or variable-size table pointers under `KEYMAP_SIZE_VARIABLE`. `struct keyboard` groups normal, shifted, caps, altgraph, numlock, control, and key-up maps with idle masks, abort sequences, toggle-shift state, exception maps, and newer abort sequences. `struct exception_map` represents modifier-sensitive overrides not expressible as ordinary keymap entries. Compose and floating-accent structures map two-step input sequences to UTF-8 keymap entries.

Encoded keymap actions use `SPECIAL(h, l)` in the top byte. Classes include shift keys, bucky bits, funny actions (`NOP`, `OOPS`, `HOLE`, `RESET`, `ERROR`, `IDLE`, `COMPOSE`, `NONL`), floating accents, string keys with `KTAB_STRLEN`, function-key groups, and keypad keys.

## Interfaces

There are no function prototypes. This file defines the data and value contract consumed by keyboard drivers, `kbtrans`, ioctl handlers, and keymap tables.

## Integration Notes

This header is a compatibility and data-format hub. Existing keymap tables depend on exact special-action encodings and modifier bits. The comments explicitly reserve some mask values and explain that keyboard-specific modules can opt into variable keymap sizes, which is essential for USB keyboards with up to 255 key entries.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbdreg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbdreg.h

## Role

`kbdreg.h` contains private keyboard implementation state shared by the keyboard translation implementation. It is not a public ioctl or user ABI header.

## Major Definitions

`struct keyboardstate` stores the current keyboard ID, ID-recognition state, scanner state, repeat key, bucky bits, shift mask, current keyboard table pointer, and toggle-shift mask. The ID recognizer states are `KID_NONE`, `KID_GOT_PREFACE`, `KID_OK`, and `KID_GOT_LAYOUT`.

## Interfaces

There are no function prototypes. Consumers use the state structure and recognizer constants internally.

## Integration Notes

This header depends on the keyboard table types from `kbd.h` and describes mutable translation/scanner state. It should remain private to keyboard implementation code because exposing or changing it affects scanner state-machine behavior and keyboard layout detection.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbdreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbio.h

## Role

`kbio.h` defines keyboard-related ioctl numbers, keymap ioctl payload structures, LED/compat/layout/autorepeat/beeper controls, and x86-specific ioctl-number offsets needed to avoid historical `kd` conflicts.

## Major Definitions

The ioctl namespace is `KIOC` as `('k' << 8)`. `KIOCTRANS`, `KIOCGTRANS`, `KIOCTRANSABLE`, and `KIOCGTRANSABLE` set/query translation mode and whether table translation is possible, with x86-compatible values offset by 30 for conflict avoidance. `TR_CANNOT` and `TR_CAN` report table translatability.

`struct kiockey` is the old-style keymap entry with an 8-bit entry value and special tablemask values for abort key stations. `struct kiockeymap` is the new-style entry with an unsigned keymap entry. `KIOCSETKEY`/`KIOCGETKEY` and `KIOCSKEY`/`KIOCGKEY` set/query keymap entries and string table values. Other ioctls control keyboard commands, type, direct-to-console routing, LEDs, compatibility mode, layout, abort behavior, autorepeat delay/rate/count, beeper frequency, and tone generation.

Abort controls define disable, hardware BREAK enable, and alternate-abort modes. `struct freq_request` selects console or keyboard beeper and a frequency; `KIOCMKTONE` uses historical i8254 clock cycles with `PIT_HZ` defined as 1193182 and aliased as `KDMKTONE`.

## Interfaces

There are no functions. The header exports ioctl request values and payload layouts for keyboard consumers and drivers.

## Integration Notes

The x86 conditional ioctl numbering is an ABI compatibility constraint. Keymap ioctl handlers must validate table masks, key stations, string lengths, and special abort-table selectors. Some ioctls are privileged or affect serial input devices as well as keyboards, especially keyboard abort configuration.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbtrans.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbtrans.h

## Role

`kbtrans.h` defines the interface between hardware keyboard drivers and the generic keyboard translation module. It keeps `struct kbtrans` and `struct kbtrans_hardware` opaque while exposing initialization, teardown, STREAMS message handling, key event delivery, LED handling, polled input, reset notification, queue management, and timeout cleanup APIs.

## Major Definitions

`KBTRANS_USBKB_DEFAULT_LAYOUT` indicates no kernel-configured USB keyboard layout, and `KBTRANS_KEYNUMS_MAX` is 255. `enum kbtrans_message_response` lets hardware drivers know whether `kbtrans` consumed a STREAMS message.

The callback surface is `struct kbtrans_callbacks`, with hardware callbacks for non-polled LED setting, polled LED setting, and polled key availability. `polled_keycode_func` and `struct hw_polledio` describe polled keycode retrieval state used by console/debugger paths.

## Interfaces

`kbtrans_streams_init()` initializes translation during the hardware driver's open path and returns opaque translation state; it accepts initial LED state/mask so firmware state such as NumLock can be preserved. `kbtrans_streams_fini()` tears it down. `kbtrans_streams_message()` processes upstream STREAMS messages and tells the hardware module whether more handling is needed.

Hardware drivers report actual key transitions through `kbtrans_streams_key()`, report keyboard type/table through `kbtrans_streams_set_keyboard()`, report resets through `kbtrans_streams_has_reset()`, and mark stream readiness with `kbtrans_streams_enable()`. Polled input uses `kbtrans_ischar()` and `kbtrans_getchar()`. Additional helpers update LED state, release all held keys, swap/get the upstream queue, and clear timeouts.

## Integration Notes

This header separates hardware scan-code delivery from generic keyboard translation and autorepeat. Hardware drivers are expected to suppress hardware-generated autorepeat and report only real press/release transitions. Polled routines are documented for single-threaded contexts such as kmdb/PROM input.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbtrans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kcpc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kcpc.h

## Role

`kcpc.h` defines the kernel-facing CPU performance counter (CPC) programming interface. It exposes the opaque `kcpc_set_t` type to all consumers and, under `_KERNEL`, the set/request structures and functions used to bind, program, sample, list, and manage hardware performance counter events.

## Major Definitions

Inside the kernel, `struct _kcpc_set` holds set flags, request count, request array, data storage, owning CPC context, bound/unbound state, mutex, and condition variable. `KCPC_SET_BOUND` marks bound state. `struct _kcpc_request` stores PCBE-specific configuration, data index, physical PIC number, context PIC pointer, data pointer, event name, preset value, flags, attributes, and a caller-owned pointer. `kcpc_request_list_t` is a dynamically managed list of counter-event requests.

Function pointer types describe a per-counter update callback and a current-CPU read function.

## Interfaces

The kernel API includes framework initialization, thread/CPU binding, sampling into user buffers with time/tick data, CPU context creation, event support checks, request-list init/add/reset/free, current-CPU read/program/unprogram operations, unbind, preset, restart, enable/disable, thread-context invalidation, overflow handling, CPU/LWP hooks, idle context installation, CPU context freeing, config iteration/invalidation/freeing, event/attribute listing, PCBE capability/loading checks, nonprivileged access checks, and PCBE registration.

It also declares global CPC CPU-context lock/count state and DTrace CPC integration globals: `dtrace_cpc_in_use` and `dtrace_cpc_fire`.

## Integration Notes

This header sits between kernel CPC consumers, DTrace, CPU context switching, and processor-specific back-end engines. Locking and state transitions are part of the exported structure contract for kernel code. Because counters can be bound to threads or CPUs and can overflow asynchronously, callers must coordinate lifecycle, invalidation, and context programming carefully.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kcpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kd.h

## Role

`kd.h` provides minimal compatibility definitions for historical `kd` display-mode ioctls. The file explicitly warns it may be deleted or changed without notice.

## Major Definitions

The ioctl namespace is `KDIOC` as `('K' << 8)`. `KDGETMODE` and `KDSETMODE` query and set text/graphics mode. Mode values are `KD_TEXT`, `KD_GRAPHICS`, and `KD_RESETTEXT`.

## Interfaces

There are no functions or structures. The header only exports compatibility ioctl constants.

## Integration Notes

This is a narrow compatibility shim. Any code using it should treat the interface as legacy and avoid extending it unless required for old consumers.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi.h

## Role

`kdi.h` defines the public part of the Kernel/Debugger Interface. It names the debugger virtual-address reservation, declares debugger vector globals, exposes kernel-to-debugger notification wrappers, and defines DTrace/kmdb breakpoint coordination state.

## Major Definitions

`kdi_segdebugbase` and `kdi_segdebugsize` describe the VA range reserved for kmdb. The file forward-declares kernel structures used across KDI and defines opaque `kdi_debugvec_t` and `kdi_t`. `kdi_dvec` points to the debugger callback vector and `kdi_dmods` tracks debugger-visible modules. `KDI_VERSION` is 7.

The DTrace/kmdb coordination model uses `kdi_dtrace_set_t` transition requests for DTrace activate/deactivate and kmdb breakpoint activate/deactivate. `kdi_dtrace_state_t` represents active DTrace, idle, or active kmdb breakpoint states. Comments document that DTrace and kmdb cannot both own breakpoints and transitions do not go directly between active states.

## Interfaces

Notification wrappers include VM-ready, memory-available, module-available, thread-available, module-loaded, and module-unloading calls, with SPARC-only CPU-init and CPR-restart notifications. `kdi_dtrace_set()` requests DTrace/kmdb state transitions.

## Integration Notes

The debugger side of the interface is architecture-specific and defined through `archkdi.h`/machine headers, while this header lets kernel code notify debugger state changes. The functions are intended for stopped-system debugger control paths and breakpoint ownership coordination, so misuse can interfere with DTrace or kmdb operation.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi_impl.h

## Role

`kdi_impl.h` defines the implementation-side Kernel/Debugger Interface structures and helper entry points. It expands the opaque public KDI types into debugger callback vectors, platform claim/release hooks, and the kernel service ops vector consumed by kmdb.

## Major Definitions

`struct kdi_debugvec` is the kernel-to-debugger vector. It includes kernel-control notifications, debugger callbacks for VM/memory/module events, x86 fault handling, and SPARC CPU/CPR callbacks where applicable. `kdi_plat_t` holds platform hooks for system and console claim/release, and macros expose those hooks through the global `kdi_plat` member.

`struct kdi` is the debugger-to-kernel service vector. It records the interface version and operations for module-change detection, module iteration, loaded/change checks, system claim/release, physical reads/writes, cache flushing, non-toxic range checks, polled console I/O acquisition, virtual-to-physical translation, DTrace state get/set, platform callback execution, kmdb entry, plus machine-specific and platform-specific embedded state.

## Interfaces

The file declares softcall/setsoftint helpers, physical read/write wrappers, range toxicity checks, cache flushing, DTrace state query, virtual-to-physical translation, CPU/machine/platform KDI initialization functions, and temporary boot KDI initialization/finalization helpers.

## Integration Notes

Most operations are intended to work while the debugger has stopped the system, so normal blocking services are unavailable. Implementations must avoid allocation and synchronization assumptions that are unsafe in debugger-control context. Architecture conditionals make this header a common contract over machine-specific debugger mechanics.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kfpu.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kfpu.h

## Role

`kfpu.h` defines the kernel API for opting into floating-point unit use. It gives kernel code a controlled way to allocate FPU state and bracket FPU usage so state can be saved/restored across context switches.

## Major Definitions

`kfpu_state_t` is an opaque kernel FPU state object. Flags for begin/end are `KFPU_NO_STATE`, meaning no explicit `kfpu_state_t` is passed and preemption-based handling is used, and `KFPU_USE_LWP`, meaning no explicit state is passed and LWP state is used.

## Interfaces

`kernel_fpu_alloc()` and `kernel_fpu_free()` manage reusable FPU state. `kernel_fpu_begin()` and `kernel_fpu_end()` bracket a thread's FPU-using region. `kernel_fpu_no_swtch()` is an internal validation hook.

## Integration Notes

The file warns that FPU use in the kernel requires care. A `kfpu_state_t` may be allocated independently from use and is not permanently thread-bound, but only one thread may use a given state object at a time. Missing or mismatched begin/end calls risk corrupting user or kernel FPU state.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kfpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv.h

## Role

`kiconv.h` defines the kernel iconv framework interfaces and internal data structures for registering and dispatching codeset conversions. Its substantive content is compiled only under `_KERNEL`.

## Major Definitions

`kiconv_code_list_t` maps normalized code names to numeric IDs. `kiconv_conv_list_t` maps a to-code/from-code pair to a module ID and conversion function pointers: open, streaming conversion, close, and string conversion. `kiconv_mod_list_t` stores module names and reference counts.

Module registration uses `kiconv_ops_t` entries, each naming a to-code/from-code pair and conversion callbacks, and `kiconv_module_info_t`, which supplies module name, conversion table, aliases/canonicals, and `nowait` behavior. `kiconv_data_t` is the conversion descriptor returned to framework consumers, storing an implementation handle and conversion-list index. `kiconv_state_data_t` stores common conversion state including an ID and whether a BOM has been processed.

The file also defines compact table component types for conversions to UTF-8 and to single-byte encodings, maximum normalized code-name length, skippable characters during code-name normalization, ASCII and UTF-8 replacement characters, and numeric module IDs for embedded, Japanese, simplified Chinese, Korean, traditional Chinese, and EMEA conversion modules.

## Interfaces

Kernel functions include `kiconv_init()`, module registration/unregistration, and module reference-count query.

## Integration Notes

The header defines a plug-in style conversion registry whose function pointers are loaded by module ID. Code-name normalization ignores `-`, `_`, `.`, and `@`, so aliases must be designed with that behavior in mind. Replacement-character policy mirrors `iconv(3C)` behavior for non-identical characters and depends on the target codeset.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cck_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cck_common.h

## Role

`kiconv_cck_common.h` provides common kernel helpers for CCK-family conversions between UTF-8 and encodings such as GB18030, Big5, EUC-TW, and UHC. Its substantive content is compiled only under `_KERNEL`.

## Major Definitions

The file defines EUC leading-byte rules, ASCII detection, UTF-8 replacement-character bytes and length, and a macro that validates the second byte of three- or four-byte UTF-8 sequences using shared min/max lookup tables. BOM-handling macros skip an initial UTF-8 signature either with conversion state (`KICONV_CHECK_UTF8_BOM`) or without state.

Error macros set `*errno`, mark the return value as `(size_t)-1`, and break, with an alternate path for invalid-input replacement when `KICONV_REPLACE_INVALID` is set. `kiconv_table_t` and `kiconv_table_array_t` represent binary-searchable conversion tables for UTF-8-to-CCK and CCK-to-UTF-8 mappings. `kiconv_utf8tocck_t` is a per-encoding callback used by common wrapper functions.

## Interfaces

The common open/close routines are `kiconv_open_to_cck()` and `kiconv_close_to_cck()`. `kiconv_binsearch()` searches conversion tables. `kiconv_utf8_to_cck()` wraps streaming conversion from UTF-8 to a CCK encoding using an encoding-specific callback, and `kiconvstr_utf8_to_cck()` provides the string-based equivalent. The header also declares UTF-8 validation lookup tables from `u8_textprep.c`.

## Integration Notes

The macros assume local variable names such as `kcd`, `ib`, `ibtail`, `errno`, `ret_val`, and `flag` in conversion implementations, so they are convenient but context-sensitive. Implementations must preserve input/output pointer bounds while using replacement and BOM-skipping paths.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cck_common.h -->