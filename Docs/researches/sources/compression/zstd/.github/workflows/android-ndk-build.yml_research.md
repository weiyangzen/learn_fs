# sources/compression/zstd/.github/workflows/android-ndk-build.yml

Purpose: GitHub Actions workflow validating zstd builds for Android arm64 using both the make build and CMake/NDK toolchain path.

Important behavior: it runs on pull requests to `dev`, `release`, and `actionsTest`, plus pushes to `actionsTest` or branches matching `*ndk*`. Steps check out the code, install JDK 17, set up the Android SDK, install NDK `27.0.12077973`, export `ANDROID_NDK_HOME`, then build with `aarch64-linux-android21-clang`, `llvm-ar`, `llvm-ranlib`, and `llvm-strip`. A second path configures `build/cmake` with the Android toolchain, ABI `arm64-v8a`, platform `android-21`, and Release build.

State, dependencies, and integration: ephemeral state is the installed NDK and `build-android` directory. It integrates top-level `make`, `build/cmake`, and Android SDK tooling.

Risks and test signals: NDK version pinning gives reproducibility but can age. The workflow tests compilation only, not runtime execution on device/emulator. It is the primary signal for Android compiler, archive tool, CMake toolchain, and minimum API compatibility.
