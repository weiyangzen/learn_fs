## sources/distributed-fs/beegfs/meta/source/program/Program.cpp

Purpose: implements static program startup. It performs build/runtime checks, constructs the metadata `App`, runs it in the current thread, captures the application result, and deletes the app.

Important APIs/functions: `App* Program::app` is the global app pointer. `Program::main` calls `BuildTypeTk::checkDebugBuildTypes`, `AbstractApp::runTimeInitsAndChecks`, `new App(argc, argv)`, `App::startInCurrentThread`, `App::getAppResult`, and `delete app`.

Control flow: initialization checks happen before `App` construction. The app runs synchronously in the caller thread; after it stops, the result code is read before deletion and returned to `main`.

State and persistence behavior: owns the process-global `Program::app` pointer for the app lifetime. This pointer is the integration point used throughout metadata server code, including session cleanup, lock notifications, PMQ logging, and dentry storage.

Dependencies and integration points: depends on `BuildTypeTk`, `AbstractApp`, and `App`. `Program::getApp` from the header exposes the static pointer to subsystems.

Risks: `app` is not reset to `NULL` after deletion, so late static/destructor code calling `Program::getApp()` would see a dangling pointer. `new App` is not checked for allocation failure.

Test signals: startup tests should validate runtime checks happen before app construction, app result propagation, and no subsystem uses `Program::getApp()` after app teardown.
