## sources/control-plane/csi-driver-nfs/test/utils/testutil/testutil.go

Purpose: provides a small test utility for building an absolute path under the current working directory. `GetWorkDirPath` reads `os.Getwd`, fails the test if it cannot, and appends the requested directory using `os.PathSeparator`.

State is process current working directory only. Dependencies are Go `os`, `fmt`, and `testing`. Integration points are unit or integration tests that need fixture paths relative to the test working directory. Risks include string concatenation instead of `filepath.Join`, behavior depending on caller working directory, and immediate `t.Fatalf` preventing caller-level recovery. Test signal is indirect through any tests using this helper.
