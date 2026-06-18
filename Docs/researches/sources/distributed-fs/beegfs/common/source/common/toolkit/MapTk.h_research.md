<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h

Purpose: Declares map utility helpers for string configs and vector maps.

Important APIs/types: `MapTk` exposes parser/load/save/copy functions and inline `stringMapRedefine` to erase and reinsert a key/value.

Control flow/state/persistence: Most logic is in the implementation. `stringMapRedefine` mutates the caller-provided map in place.

Dependencies/integration: Includes common map/list aliases. Used by configuration and utility code.

Risks/test signals: Tests should cover redefinition preserving only one key, missing file exceptions, and pointer-map copy ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h -->
