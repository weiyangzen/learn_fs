<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h

## Purpose

`hpi.h` defines the public AudioScience Hardware Programming Interface used by the ASI driver stack. It is a low-level adapter abstraction for digital audio hardware, describing public constants, enum values, packed data structures, and function prototypes for subsystem discovery, adapter management, streams, mixers, controls, and format creation. `asihpi.c` consumes these definitions to map HPI capabilities to ALSA devices and controls.

## Important APIs, Types, and Functions

- Format and stream enums: `enum HPI_FORMATS`, `enum HPI_STREAM_STATES`, MPEG ancillary/mode enums, and `struct hpi_format`.
- Mixer graph enums: `enum HPI_SOURCENODES`, `enum HPI_DESTNODES`, and `enum HPI_CONTROLS` define node/control identifiers used to enumerate mixer topology.
- Adapter properties and modes: `enum HPI_ADAPTER_PROPERTIES`, `enum HPI_ADAPTER_MODE_CMDS`, `enum HPI_ADAPTER_MODES`, and capability macros.
- Control attributes: volume units and sentinels, AES/EBU formats/errors, tuner bands/modes/status, channel modes, sample-clock sources, filter types, async event sources, and PAD string lengths.
- Errors and limits: `enum HPI_ERROR_CODES`, `HPI_MAX_ADAPTERS`, `HPI_MAX_STREAMS`, `HPI_MAX_CHANNELS`, `HPI_MAX_ANC_BYTES_PER_FRAME`, and related constants.
- Packed structures: `struct hpi_format`, `struct hpi_anc_frame`, and `struct hpi_async_event`.
- Public functions: subsystem discovery (`hpi_subsys_*`), adapter open/close/info/property/mode APIs, outstream/instream open/read/write/start/stop/reset/query/group/host-buffer APIs, mixer open/get-control/store APIs, and control-specific volume, meter, tuner, AES/EBU, mux, sample-clock, microphone, EQ, compander, Cobranet, tone/silence detector, and `hpi_format_create()` APIs.

## Control Flow

The header has no executable control flow, but it defines the command surface used by HPI implementations and clients. Typical control flow begins with subsystem/adapter discovery, opening an adapter, querying adapter info/properties, opening streams or the mixer, querying formats or controls, then issuing stream data movement or control get/set commands. Stream operations are handle-based: outstream and instream handles are opened by adapter index/stream index and later passed to read/write/start/stop/reset/group/host-buffer functions. Mixer control flow is mixer-handle based and then control-handle based.

## State and Persistence Behavior

The header defines state identifiers but stores no state. Persistent or nonvolatile behavior appears only as API contracts, notably adapter mode/SSX2 settings, mixer store commands, nonvolatile memory error codes, firmware update capability, and adapter properties. Runtime state such as stream stopped/playing/recording/drained, async event sequence, mixer control values, and sample clock source is maintained by HPI implementation code and hardware.

## Dependencies and Integration Points

`hpi.h` includes Linux integer types and defines `HPI_BUILD_KERNEL_MODE`, making it a kernel-mode HPI API header. It integrates with internal HPI implementation files (`hpifunc`, message dispatch, adapter backends) and ALSA-facing code. It also carries comments about Windows equivalents for formats, indicating the API is cross-platform in origin even though this copy is kernel-facing.

## Risks and Edge Cases

- Enum values are ABI-like: comments warn that adding source/destination/control types requires updating debug tables and that control types above 255 affect DSP bit packing.
- Packed structure layout matters for message compatibility.
- Some names contain historical spellings or aliases; callers must use numeric values consistently.
- Error-code ranges are constrained: driver errors, adapter errors, stream errors, mixer/control errors, ioctl mutex timeout, and backend compatibility all share one enum.
- Many APIs accept raw pointers and fixed-size arrays, so callers must ensure buffer sizes and channel counts match HPI expectations.
- HPI supports both local and networked adapters; adapter indexes >= 100 are reserved for networked adapters.

## Test Signals

Compile-time validation should confirm all users see matching enum ranges and structure layouts. Functional tests should exercise `hpi_format_create()`, adapter property queries used by `asihpi.c`, stream open/read/write/start/stop/reset/group/host-buffer calls, mixer enumeration/control get-set paths, sample-clock source/rate queries, error-code translation, and async event structures where supported by backend hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi.h -->
