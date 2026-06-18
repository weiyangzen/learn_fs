# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/libgfchangelog.py

Purpose: this Python module is a minimal ctypes wrapper around `libgfchangelog`. It exposes class methods for initialization, registration, scanning, tracker reset, fetching changes, and marking changes done.

Important APIs: `Changes.libgfc` loads `gfchangelog` with `RTLD_GLOBAL` and `use_errno=True`. `_get_api` fetches C symbols. `cl_init`, `cl_register`, `cl_scan`, `cl_startfresh`, `cl_getchanges`, and `cl_done` call the corresponding C functions and raise `OSError` on `-1`.

Control flow: `cl_getchanges` allocates a 4096-byte buffer, repeatedly calls `gf_changelog_next_change`, appends returned byte slices without the trailing NUL/newline, raises on `-1`, resets the tracker through `cl_startfresh`, and returns the sorted list using the suffix after the last dot as the key.

State and persistence behavior: wrapper state is process-global through the loaded C library and its `THIS`/API state. It does not manage files directly, but `cl_done` delegates persistent movement to `gf_changelog_done`.

Dependencies and integration points: uses `ctypes`, `ctypes.util.find_library`, and errno propagation from the C library. It is intended for the adjacent `changes.py` example.

Risks: `cl_init` calls `raise_changelog_err`, which is not defined in the class; this is a bug on init failure. Python 3 ctypes calls are passed Python strings unless callers encode them; depending on runtime, bytes may be required for C `char *` arguments. Return types and argument types are not declared, so ctypes defaults can be unsafe on platforms where sizes differ.

Test signals: import when `libgfchangelog` is installed, force init/register failure to validate error paths, pass bytes and string arguments under Python 3, scan and fetch more than one change, and verify tracker reset plus sorted order.
