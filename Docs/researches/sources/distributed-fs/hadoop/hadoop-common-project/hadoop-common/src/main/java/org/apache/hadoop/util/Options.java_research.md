# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Options.java

## Purpose

`Options` provides type-safe marker classes for varargs option lists and helpers to retrieve or prepend options.

## Important APIs, Types, And Functions

Nested abstract option classes carry values for `String`, `Class`, `boolean`, `int`, `long`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, and `Progressable`. `getOption(Class<T>, base[] opts)` returns the first option assignable to a class. `prependOptions(T[] oldOpts, T... newOpts)` combines arrays with new options first.

## Control Flow, State, And Persistence

Each option wrapper stores a final value and exposes it through a getter. `getOption()` scans the varargs array and casts the first matching class. `prependOptions()` uses `Arrays.copyOf()` and `System.arraycopy()`. There is no global state or persistence.

## Dependencies And Integration Points

It depends on Hadoop filesystem stream/path types and `Progressable`. Filesystem APIs use it to accept extensible typed optional arguments without long overload lists.

## Risks And Test Signals

Matching by class means subclasses and duplicate option types return the first matching instance. Tests should cover all wrapper getters, absent options, subclass matching, duplicate ordering, null arrays if allowed by callers, and prepend order/array component type.
