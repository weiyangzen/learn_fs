# sources/distributed-fs/ceph-client/scripts/jobserver-exec

## Purpose
Runs a subprocess after reserving all available GNU make jobserver tokens and passes the reserved capacity via `PARALLELISM`.

## APIs, Control Flow, and State
The Python CLI expects `command [args ...]`. It prepends `../tools/lib/python` relative to the script location to `sys.path`, imports `JobserverExec`, and uses it as a context manager. Inside the context, `jobserver.run(sys.argv[1:])` executes the requested command. The context manager owns token acquisition/release and environment setup; this wrapper stores no state itself.

## Dependencies and Integration
It depends on Python 3, the kernel `tools/lib/python/jobserver.py` implementation, GNU make jobserver file descriptors/environment, and the child command honoring `PARALLELISM`.

## Risks and Test Signals
Risks include incorrect relative library paths, running outside make without jobserver metadata, or child commands ignoring the variable. Test signals are child execution under parallel make, no token leaks after failures, and fallback behavior from `JobserverExec`.
