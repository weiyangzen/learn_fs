# sources/distributed-fs/openafs/src/gtx/object_test.c

Purpose: manual test driver for GTX object operations across selectable window packages.

Important functions: `test_objects` initializes the requested backend, creates four light objects and one text object, toggles lights, writes strings to the text object, and scrolls it. `object_testInit` parses `-package` and `-debug`; `main` registers command syntax and dispatches.

Control flow and state: command-line parsing chooses backend, then `gator_objects_init` calls `gw_init`. The test creates objects using repeated parameter struct mutation, displays them via `OOP_DISPLAY`, writes text with sleeps between operations, scrolls up/down, and finally calls `WOP_CLEANUP`.

Dependencies and integration: includes object/window headers and `afs/cmd.h`; depends on backend globals such as `gator_basegwin`. It references `gtxscreenobj.h`, though the researched object code focuses on text/light.

Risks: old-style K&R declarations and `%x` pointer formatting are present. It lacks assertions and has an unconditional error print in the scroll-down loop even when no error occurs. The dumb backend path cannot create usable windows. Test signals are visual/manual: object creation, light toggling, text wrapping, highlighted lines, scroll bounds, and backend cleanup.
