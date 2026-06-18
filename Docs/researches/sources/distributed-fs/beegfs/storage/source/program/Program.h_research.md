<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.h -->
## sources/distributed-fs/beegfs/storage/source/program/Program.h

### Purpose
Declares the process-level Program singleton wrapper used to access the running storage App.

### Important APIs, Types, And Functions
Public APIs are static main(int, char**) and static getApp(). The constructor is private and the static App* app is defined in Program.cpp.

### Control Flow
The header establishes Program as the central access point used by message handlers, stores, quota helpers, and target management.

### State, Persistence, And Dependencies
The only state is the static App pointer. Depends on app/App.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is broad global coupling and lack of null-safety in getApp(); most storage code assumes App has already been constructed.

### Test Signals
Test signals include singleton availability during App lifetime and compilation of modules that include Program.h.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.h -->
