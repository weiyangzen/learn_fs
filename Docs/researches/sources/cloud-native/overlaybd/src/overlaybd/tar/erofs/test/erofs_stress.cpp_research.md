# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress.cpp

Purpose: randomized stress test suite for multi-layer EROFS construction from tar layers. It validates metadata, xattrs, content hashes, overwrite semantics, same-name upper/lower entries, whiteouts, and delete-then-recreate scenarios.

Important APIs/types/functions: `StressInterImpl` implements `StressGenInter` with random content generation, xattr creation/listing, mode/ownership/mtime generation, directory metadata, stat capture, content hashing, and name generation. `StressCase001` through `StressCase009` specialize the generator for specific coverage goals. `TEST(ErofsStressTest, TC001..TC009)` instantiates each case with different layer counts and tree sizes.

Control flow: each test seeds `rand()` with current time, constructs a case rooted at `./erofs_stress_NNN`, calls `StressBase::run`, then deletes the case. The base runner builds one tar layer at a time, updates an in-memory expected tree, converts layers into stacked LSMT images, extracts with `LibErofs`, mounts with `create_erofs_fs`, and asks the generator to reconstruct observed metadata/content from the mounted filesystem for comparison.

State and persistence: test data is persisted in relative work directories such as `./erofs_stress_006`, with generated layer tar files plus `.idx` and `.meta` LSMT sidecars. Successful runs remove the directory through `StressBase::run`; failures leave artifacts for diagnosis. Randomized names, xattrs, file contents, uid/gid, and mtimes are captured into `StressNode` records for later verification.

Dependencies/integration: integrates gtest, Photon runtime, Photon FS/xattr APIs, GNU tar command-line behavior via the base class, LSMT warp/stack files, `LibErofs`, and EROFS Photon filesystem mounting. It depends heavily on filesystem xattr support and external `tar` with `--xattrs`.

Risks: tests are nondeterministic because they seed from wall time and use `random_device`, so reproducing failures requires captured artifacts. Some comments do not match actual layer sizes, for example TC001 describes 50 files but returns small counts. The suite can be expensive: TC009 generates 1000 directory nodes per layer. The helper macro hides unimplemented metadata paths, so each case only validates the fields it explicitly enables.

Test signals: TC001 checks basic tree integrity, TC002 file content, TC003 file and directory xattrs, TC004 mode, TC005 uid/gid/mtime through stat, TC006 combined metadata/content, TC007 same-name replacement, TC008 whiteouts, and TC009 deletion followed by name reuse.
