<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.cpp -->
## sources/distributed-fs/beegfs/storage/source/program/Program.cpp

### Purpose
Owns top-level process startup and shutdown for the storage daemon App singleton.

### Important APIs, Types, And Functions
Defines static Program::app and Program::main(). Program::main() checks build-type compatibility, runs AbstractApp runtime initialization, creates App(argc, argv), starts it in the current thread, captures getAppResult(), deletes the App, and returns the result.

### Control Flow
Control flow is linear: initialize runtime, construct App, run until App exits, read result, destroy App. Program::getApp() exposes the static pointer to the rest of the storage code while App is alive.

### State, Persistence, And Dependencies
Program::app is process-global runtime state. No persistent data is written here directly, but App startup/shutdown drives all daemon persistence. Depends on BuildTypeTk, AbstractApp, App, and Program.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include global singleton lifetime: code using Program::getApp() during shutdown after delete would dereference stale memory because app is not reset to null.

### Test Signals
Test signals include startup failure propagation, App result propagation, debug/release build-type checks, and no Program::getApp() use after Program::main() returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.cpp -->
