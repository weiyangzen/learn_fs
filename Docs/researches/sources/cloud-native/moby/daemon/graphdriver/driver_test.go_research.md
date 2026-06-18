# sources/cloud-native/moby/daemon/graphdriver/driver_test.go

Purpose: unit test for graphdriver prior-state directory emptiness detection.

Important APIs and control flow: `TestIsEmptyDir` creates a temp root, then checks `isEmptyDir` for an empty directory, a directory containing a subdirectory, and a directory containing an empty file.

State, dependencies, and risks: the test uses only local filesystem operations and `gotest.tools` assertions. It protects `scanPriorDrivers` from treating empty driver directories as prior state while recognizing any real child entry as non-empty. It does not cover read errors, nonexistent directories, duplicate drivers, removed-driver errors, or priority selection.
