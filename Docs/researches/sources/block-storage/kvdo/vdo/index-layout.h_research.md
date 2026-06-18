# File Research: sources/block-storage/kvdo/vdo/index-layout.h

Public interface for UDS index layout storage.

Key responsibilities:
- Forward-declares opaque `struct index_layout`.
- Declares layout lifecycle: `make_uds_index_layout()` and `free_uds_index_layout()`.
- Declares backing-store replacement through `replace_index_layout_storage()`.
- Declares clean-state persistence APIs: `load_index_state()`, `save_index_state()`, `discard_index_state_data()`, and `discard_open_chapter()`.
- Declares accessors for volume nonce and dm-bufio access to the volume region.

Dependencies:
- Includes `buffer.h`, `config.h`, `io-factory.h`, and `uds.h`.
- Exposes `struct uds_index` in function signatures without defining it here.

Notable risks:
- The API is stateful and opaque; callers rely on implementation-side validation and correct save-slot ordering.
- `discard_index_state_data()` lacks `__must_check`, unlike most mutating persistence calls.
