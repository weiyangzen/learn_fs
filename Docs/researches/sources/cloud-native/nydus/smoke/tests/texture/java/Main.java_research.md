# sources/cloud-native/nydus/smoke/tests/texture/java/Main.java

## Purpose
This Java texture program is used by container smoke tests to validate that a mounted Java source file can be compiled and executed inside a Java-capable image.

## Important APIs, Types, And Functions
It defines class `Main` with `public static void main(String[] args)` and prints `hello` using `System.out.println`.

## Control Flow
The JVM enters `Main.main`, writes one line to stdout, and exits.

## State And Persistence
The source file itself is read by `javac`. Runtime state is transient, though compilation creates `Main.class` in `/src`.

## Dependencies And Integration Points
It is compiled and run by `texture/java/entrypoint.sh`, which is mounted for the `amazoncorretto` recipe in `tool/container.go`.

## Risks
The program is intentionally minimal and cannot detect nuanced filesystem issues beyond source readability and class file write support in the mounted directory.

## Test Signals
A successful `javac Main.java` followed by `java Main` indicates the mounted source directory is accessible and executable in the Java container.
