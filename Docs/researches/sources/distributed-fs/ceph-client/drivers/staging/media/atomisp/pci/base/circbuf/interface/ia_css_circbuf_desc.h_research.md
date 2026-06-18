# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_desc.h

Purpose: provides inline operations on the circular-buffer descriptor independent of the backing element array.

Important APIs/types/functions: functions include `ia_css_circbuf_desc_is_empty()`, `ia_css_circbuf_desc_is_full()`, `ia_css_circbuf_desc_init()`, `ia_css_circbuf_desc_get_pos_at_offset()`, `ia_css_circbuf_desc_get_offset()`, `ia_css_circbuf_desc_get_num_elems()`, and `ia_css_circbuf_desc_get_free_elems()`.

Control flow: helpers compute modular positions with `OP_std_modadd()`, normalize negative offsets by adding `size`, and derive occupancy from `start` to `end`.

State and persistence: only the descriptor's runtime fields are read or initialized. `desc_init()` sets `size` but leaves `start`, `end`, and `step` for `ia_css_circbuf_create()`.

Dependencies and integration: included by the main circular-buffer interface and uses CSS math/assert/platform helpers.

Risks and test signals: callers must avoid zero sizes before modular arithmetic. `get_free_elems()` does not account for the unusable padding slot, which can surprise users of the lockless full/empty convention. Tests should cover zero-size rejection by assertions, wrap offsets, and full/empty boundaries.
