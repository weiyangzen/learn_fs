# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/moving.rs

- RAII wrapper around C `moving_context`.
- Allocates and pins the context because initialized list heads become self-referential.
- Initializes through `bch2_moving_ctxt_init`, exposes unsafe `move_data_btree`, and exits through `bch2_moving_ctxt_exit` on drop.
