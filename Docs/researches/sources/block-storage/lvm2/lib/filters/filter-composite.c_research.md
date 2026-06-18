# File Research: sources/block-storage/lvm2/lib/filters/filter-composite.c

This file implements a composite device filter that ANDs together a sequence of `struct dev_filter` instances. `composite_filter_create` copies the supplied filter pointer array, appends a NULL terminator, allocates the wrapper filter, and assigns name `composite`.

`_and_p` enables external device info for the duration of filtering, then invokes each child filter unless `use_filter_name` selects a specific child by name. The first failing child stops evaluation and returns failure without treating filter rejection as an internal error.

`_wipe` forwards cache/device wipe requests to child filters that implement a `wipe` method, honoring `use_filter_name`. `_composite_destroy` warns if the filter is still in use, destroys all child filters, then frees the copied array and wrapper.

The composite filter is the coordination point for ordered filter chains; the order of the child array determines which rejection reason is observed first.
