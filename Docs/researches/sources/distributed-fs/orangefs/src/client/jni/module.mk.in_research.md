<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/module.mk.in -->
# sources/distributed-fs/orangefs/src/client/jni/module.mk.in

## Purpose

`module.mk.in` wires the OrangeFS JNI component into the broader OrangeFS build when `BUILD_JNI` is enabled. It identifies native C sources and Java sources that belong to the JNI/user-interface library.

## Important APIs, Types, and Functions

Important variables are `JNI_DIR`, `JNI_JAVA_DIR`, `ORGDIR`, `USRC`, `JNIJAVA`, and `ULIBSRC`. `USRC` includes `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`; `JNIJAVA` lists POSIX/stdio wrappers, flags, stat classes, `Orange`, stream/channel classes, and layout enum support.

## Control Flow

The surrounding make system includes this fragment, checks `BUILD_JNI`, appends native sources to `ULIBSRC`, and uses the Java source list when packaging or installing the JNI Java interface.

## State, Persistence, and Concurrency

This is build metadata only. It produces native and Java artifacts but stores no runtime state.

## Dependencies and Integration Points

It integrates the JNI directory with OrangeFS's top-level build and must stay synchronized with Maven packaging and Java native declarations.

## Risks and Test Signals

Missing a Java class or C file here can make autotools builds differ from Maven/manual builds. Test by building with `BUILD_JNI` enabled and verifying the resulting jar/native library contain the same API surface expected by Hadoop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/module.mk.in -->
