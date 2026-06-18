# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/changes.py

Purpose: this Python example wraps the ctypes changelog binding in a polling loop. It initializes the library, registers one brick, repeatedly scans for changes, prints them, and marks each change done.

Important functions: `get_changes` accepts brick, scratch directory, log file, log level, and polling interval. It calls `Changes.cl_init`, `cl_register`, `cl_scan`, `cl_getchanges`, and `cl_done`.

Control flow: the program validates command-line arity, then enters an infinite loop inside `get_changes`. Each iteration scans, fetches all current changes from the wrapper, prints a list if non-empty, calls done for each file, and sleeps for the requested interval. `OSError` from the wrapper is caught and printed.

State and persistence behavior: persistent state is managed by `libgfchangelog`; this file only controls the poll cadence and calls `done` after printing each change. `cl_getchanges` in the wrapper also resets the tracker through `cl_startfresh`.

Dependencies and integration points: imports local `libgfchangelog.py`, plus `os`, `sys`, and `time`. It demonstrates a Python consumer path for the same C API used by native examples.

Risks: the usage string checks for six arguments but documents four user parameters, and the code uses `sys.argv[4]` as interval while passing a fixed log level, which suggests the usage text or arity is stale. It does not expose retry count. The global `cl` instance makes the sample single-client.

Test signals: run with valid brick/scratch/log/interval parameters, trigger changelog files, observe printed byte-string paths, verify `cl_done` moves files, and exercise errno propagation by using bad paths.
