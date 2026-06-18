<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/Whitebox.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/Whitebox.java

## Purpose

`Whitebox.java` is a test-only reflection helper for reading and writing private fields in target objects or classes.

## Important APIs, Types, and Functions

Public helpers are `getInternalState(Object target, String field)` and `setInternalState(Object target, String field, Object value)`. Private helpers `getFieldFromHierarchy` and `getField` locate fields through the class hierarchy and set accessibility.

## Control Flow

The public methods derive the target class, locate the named field by walking superclasses, call `setAccessible(true)`, then read or write the field. Reflection exceptions are wrapped in `RuntimeException`.

## State and Persistence Behavior

The helper owns no state. It mutates target object/class fields directly and can therefore alter static or instance state in the tested code for the lifetime of the JVM.

## Dependencies and Integration Points

It depends only on `java.lang.reflect.Field` and is a general integration point for Hadoop tests that need white-box access to internals.

## Risks and Edge Cases

Reflection bypasses encapsulation and can break under module access restrictions, security managers, renamed fields, or final-field semantics. Runtime exception wrapping can hide checked reflection details.

## Test Signals

Useful signals are superclass field lookup, static-field access through `Class` targets, missing-field failures, and successful mutation/readback of private fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/Whitebox.java -->
