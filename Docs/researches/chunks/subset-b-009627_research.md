# sources/user-network-fs/impacket/impacket/hresult_errors.py lines 5002-5877

## Purpose

This chunk is the tail of Impacket's HRESULT catalog. It defines module-level symbolic constants for Windows error/status values from the `[MS-ERREF]` HRESULT namespace, starting in the Windows Media/DVD and portable-device range and ending at the last graphics/monitor constant in the file.

The file has two related surfaces:

- `ERROR_MESSAGES`, defined earlier in the file, maps integer HRESULT values to `(symbol, message)` tuples for diagnostic lookup.
- The flat constants section, which starts after `ERROR_MESSAGES`, exposes names such as `NS_E_WMP_ACCESS_DENIED` and `ERROR_GRAPHICS_INVALID_VIDPN_TOPOLOGY` as importable integer aliases.

Lines 5002-5877 are entirely in the second surface. They do not add lookup logic or messages, but they make the late `[MS-ERREF]` symbols available to code that prefers named constants over raw hex values.

## High-Level Structure

- Lines 5002-5034: Continues Windows Media Player conversion, DVD playback, copy-protection, CD burner, PDA, and IMAPI synchronization constants, beginning with `NS_E_DVD_DISC_COPY_PROTECT_OUTPUT_NS = 0xC00D1160`.
- Lines 5035-5146: Defines Windows Media Player, WMDM, codec, DRM, network, CD, sync wizard, background-download, cURL helper, subscription/content-partner, namespace, cache, publishing point, playlist, datapath, server plugin, logging, and capture/encoding constants.
- Lines 5147-5439: Defines Windows Media Encoder profile, input, device-control, audio/video format, multipass, timecode, and source-group validation constants, then enters a large DRM block beginning at `NS_E_DRM_INVALID_APPLICATION = 0xC00D2711`.
- Lines 5440-5635: Continues DRM store, license, individualization, backup/restore, migration, certificate, proximity, output-protection, setup, and streaming/network-protocol constants.
- Lines 5636-5660: Defines playlist termination and metadata/property-query constants such as `NS_E_PROPERTY_NOT_FOUND`, `NS_E_METADATA_FORMAT_NOT_SUPPORTED`, and `NS_E_METADATA_CANNOT_RETRIEVE_FROM_OFFLINE_CACHE`.
- Lines 5661-5877: Switches from `NS_E_*` media/network constants to monitor and graphics constants in the `0xC026****` facility, ending at `ERROR_GRAPHICS_ONLY_CONSOLE_SESSION_SUPPORTED = 0xC02625E0`.

## Important APIs, Types, And Data

There are no functions or classes in this chunk. The important API is the set of public module globals created by assignment.

Representative constant families:

- DVD and media-device errors: `NS_E_DVD_COPY_PROTECT`, `NS_E_DVD_INVALID_DISC_REGION`, `NS_E_PDA_DEVICE_FULL`, `NS_E_PDA_CANNOT_TRANSCODE`, and `NS_E_IMAPI_MEDIUM_INVALIDTYPE`.
- Windows Media Player and codec errors: `NS_E_WMP_UNSUPPORTED_FORMAT`, `NS_E_WMP_CODEC_NEEDED_WITH_4CC`, `NS_E_WMP_SERVER_UNAVAILABLE`, `NS_E_WMP_AUDIO_CODEC_NOT_INSTALLED`, and `NS_E_WMP_VIDEO_CODEC_NOT_INSTALLED`.
- WMP/WMDRM and DRM lifecycle errors: `NS_E_WMP_DRM_LICENSE_EXPIRED`, `NS_E_DRM_INVALID_LICENSE`, `NS_E_DRM_NO_RIGHTS`, `NS_E_DRM_LICENSE_UNUSABLE`, `NS_E_DRM_DEVICE_NOT_REGISTERED`, and `NS_E_DRM_CERTIFICATE_REVOKED`.
- Streaming and server errors: `NS_E_UNKNOWN_PROTOCOL`, `NS_E_SERVER_UNAVAILABLE`, `NS_E_PROXY_TIMEOUT`, `NS_E_FIREWALL`, `NS_E_MMS_NOT_SUPPORTED`, and `NS_E_PUSH_CANNOTCONNECT`.
- Metadata/query errors: `NS_E_PROPERTY_NOT_FOUND`, `NS_E_PROPERTY_READ_ONLY`, `NS_E_INVALID_QUERY_OPERATOR`, `NS_E_METADATA_NOT_AVAILABLE`, and `NS_E_METADATA_INVALID_DOCUMENT_TYPE`.
- Monitor/graphics errors: `ERROR_MONITOR_INVALID_DESCRIPTOR_CHECKSUM`, `ERROR_GRAPHICS_INVALID_DISPLAY_ADAPTER`, `ERROR_GRAPHICS_NO_VIDEO_MEMORY`, `ERROR_GRAPHICS_INVALID_VIDPN_TOPOLOGY`, `ERROR_GRAPHICS_MONITOR_NOT_CONNECTED`, `ERROR_GRAPHICS_OPM_NOT_SUPPORTED`, and `ERROR_GRAPHICS_DDCCI_INVALID_MESSAGE_CHECKSUM`.

The values are Python `int` objects. Their sign is not converted to signed 32-bit representation; HRESULTs such as `0xC00D1160` and `0xC02625E0` remain positive Python integers. Callers comparing against packed wire values or Windows APIs must use the same unsigned numeric representation or explicitly normalize signed inputs.

## Control Flow

This chunk has no runtime branching, loops, function calls, imports, or exception handling. Python executes each assignment exactly once during module import. After import, consumers read constants directly from `impacket.hresult_errors`.

The only "flow" to preserve is ordering and completeness:

1. The earlier `ERROR_MESSAGES` dictionary is created first.
2. The constants section starts after the dictionary and binds each HRESULT symbol in file order.
3. This chunk completes that constants section and reaches EOF, so no later code transforms or validates the constants.

Because the assignments are independent, changing one line affects only that one symbol unless two symbols are intentionally expected to share a value elsewhere in the file. This range does not define aliases via references to earlier names; each name is assigned a literal hex integer.

## State And Persistence Behavior

- State is import-time module state only. Each assignment adds or replaces a key in the module globals dictionary.
- There is no on-disk persistence, no cache file, no mutable collection in this chunk, and no external side effect beyond imported module globals.
- Re-import uses normal Python module caching through `sys.modules`; the assignments run once per interpreter process unless the module is reloaded.
- The constants are not frozen. Python callers could monkey-patch names on the module, so tests that require catalog integrity should import a fresh interpreter or reload the module before checking exact values.
- `ERROR_MESSAGES` is not updated by these assignments. If a constant is corrected here but the earlier dictionary is not corrected, symbolic access and lookup-message access can diverge.

## Dependencies And Integration Points

This chunk has no direct imports or library dependencies. Its dependency is semantic: the numeric values and symbolic names are intended to mirror Microsoft's `[MS-ERREF]` HRESULT definitions.

Integration points are module consumers that need named HRESULTs:

- DCERPC, COM, SMB, or Windows protocol helpers can compare numeric return codes against these globals rather than embedding raw integers.
- Error-formatting code can use `ERROR_MESSAGES` for descriptions and these constants for readable comparisons in tests or protocol branches.
- Downstream applications importing Impacket can reference constants such as `NS_E_BAD_REQUEST` or `ERROR_GRAPHICS_OPM_INVALID_HANDLE` without maintaining their own HRESULT table.

The file comment says "Ideally all the files should grab the error codes from here", which positions this module as a central catalog. This chunk is therefore data infrastructure rather than protocol logic.

## Risks And Edge Cases

- Catalog drift is the primary risk. The file appears generated or mechanically copied from `[MS-ERREF]`; manual edits can introduce wrong hex values, misspell names, or omit gaps in the official table.
- There is no runtime validation that each constant has a matching `ERROR_MESSAGES` entry. A named constant may be usable for comparisons even if lookup formatting lacks the matching message, or vice versa.
- Names are close to official Windows identifiers but include existing spelling quirks from the source table, such as `NS_E_METADATA_LANGUAGE_NOT_SUPORTED`. Correcting spelling would be a breaking API change for callers that import the current symbol.
- Some constants are very similar across families, for example WMP DRM names in the `0xC00D11xx` and `0xC00D12xx` ranges and generic DRM names in the `0xC00D27xx` to `0xC00D28xx` ranges. Tests should avoid assuming that similar names imply identical values or interchangeable semantics.
- The unsigned Python integer representation can surprise code that receives signed HRESULTs from ctypes or packed protocol fields. Comparisons should normalize to 32-bit unsigned values when needed.
- The late graphics constants include long identifiers such as `ERROR_GRAPHICS_EMPTY_ADAPTER_MONITOR_MODE_SUPPORT_INTERSECTION` and `ERROR_GRAPHICS_DDCCI_CURRENT_CURRENT_VALUE_GREATER_THAN_MAXIMUM_VALUE`; mechanical line wrapping or formatting changes could accidentally alter the identifier text.
- Because this is EOF, adding new constants after line 5877 changes the module's public surface and should be coordinated with any generated-source process rather than appended casually.

## Test Signals

- Import smoke test: `import impacket.hresult_errors as h` should succeed, proving every assignment in the constants tail is syntactically valid.
- Boundary value checks should cover the start and end of this chunk, for example `h.NS_E_DVD_DISC_COPY_PROTECT_OUTPUT_NS == 0xC00D1160` and `h.ERROR_GRAPHICS_ONLY_CONSOLE_SESSION_SUPPORTED == 0xC02625E0`.
- Family checks should sample each major range: WMP, PDA/sync, cURL/content partner, namespace/cache/publishing point, encoder/source-group, DRM, streaming/network, metadata, monitor, and graphics.
- Cross-surface checks should compare selected constants against `ERROR_MESSAGES` keys and names when entries exist, such as verifying the same integer key resolves to the same symbol string in the earlier dictionary.
- Unsigned-normalization tests should assert that HRESULT values above `0x80000000` compare equal after masking signed inputs with `0xffffffff`.
- Static catalog tests can parse the assignment section and flag duplicate names, non-hex literals, missing `NS_E_*` or `ERROR_GRAPHICS_*` families, and values that do not match the authoritative `[MS-ERREF]` source used by the project.
