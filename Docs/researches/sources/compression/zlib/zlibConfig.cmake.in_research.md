# sources/compression/zlib/zlibConfig.cmake.in

`zlibConfig.cmake.in` is the config-mode CMake package template for `find_package(ZLIB)`. It validates and loads supported components and reports package-not-found messages when requested targets are unavailable.

It defines `_ZLIB_supported_components` as `shared` and `static`. With `ZLIB_FIND_COMPONENTS`, it validates each component, optionally includes `ZLIB-${_comp}.cmake` with a result variable, sets `ZLIB_${_comp}_FOUND`, and marks `ZLIB_FOUND` false on unsupported or missing components. Without components, it optionally includes both component files and then requires `TARGET ZLIB::ZLIB` and `TARGET ZLIB::ZLIBSTATIC`, emitting guidance when either is missing.

State is limited to CMake configure variables and imported targets in the consumer build graph. Integration points are exported `ZLIB-shared.cmake`/`ZLIB-static.cmake` files and the `test/find_package*.cmake.in` templates. Risks include surprising no-component failure for single-variant builds, component-name drift, and CMake package variable semantics. Test signals are positive component lookups, no-component lookup when both targets exist, and negative failure for `COMPONENTS wrong REQUIRED`.
