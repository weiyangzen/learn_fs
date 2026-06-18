# File Research: sources/block-storage/kvdo/vdo/record-page.h

Read completely: 42 lines.

This header declares record-page encoding and lookup helpers for UDS volume chapters. `encode_record_page()` converts a record array into on-disk page layout, and `search_record_page()` finds chunk metadata by name in an encoded page.

Dependencies: `common.h`, `volume.h`, UDS chunk record/name/data types, and volume geometry.

Research notes: the public contract makes record pages an encoded searchable structure rather than a raw sorted array.
