# sources/control-plane/mayastor/test/grpc/package.json

## Purpose
`package.json` defines the Node.js package used by Mayastor/io-engine gRPC tests. It gives the package name `mayastor-test`, version `0.1.0`, BSD-2-Clause license, lint scripts, runtime/test dependencies, dependency overrides, and semistandard environment settings for Mocha and Node globals.

## Important APIs, Types, and Functions
The executable surface is script based. `npm run check` runs `semistandard --verbose`; `npm run fix` runs `semistandard --fix`. The dependency set supports two styles of gRPC testing: real or mocked protobuf RPC interaction through `grpc-kit`, `grpc-mock`, `grpc-promise`, `@grpc/grpc-js`, `@grpc/proto-loader`, and the deprecated native `grpc`; and process-oriented integration helpers through `find-process`, `pidof`, `inpath`, `read`, `systeminformation`, and `wtfnode`. `chai`, `mocha`, `async`, `lodash`, `glob`, and `sleep-promise` provide the local assertion and async test utility layer.

## Control Flow, State, and Persistence
The manifest has no application control flow. It controls npm install resolution, available npm scripts, and lint behavior. Dependency state is persisted in `package-lock.json`; the manifest supplies ranges while the lock pins concrete versions. The `semistandard.env` setting allows test files to use Mocha and Node globals without lint failures.

## Dependencies and Integration Points
This package is tightly coupled to the JavaScript files in `sources/control-plane/mayastor/test/grpc`, the Rust debug binaries under `sources/control-plane/mayastor/target/debug`, and the protobuf definition under `utils/dependencies/apis/io-engine/protobuf/mayastor.proto`. The `overrides` block forces `serialize-javascript >=7.0.5` and `tar ^7.5.11`, which is likely intended to keep transitive security fixes in place while preserving the existing test dependency stack.

## Risks
The manifest mixes old and new gRPC stacks. Keeping both `grpc` and `@grpc/grpc-js` increases install risk because `grpc` is deprecated and native-install sensitive, while the tests mostly depend on command-line behavior rather than a pure JS API boundary. The overrides can raise the effective Node.js floor: the locked `serialize-javascript` requires Node >=20 and `tar` 7.x requires Node >=18. No `test` script is declared, so CI must invoke Mocha explicitly elsewhere; otherwise this package can pass lint without running behavioral tests.

## Test Signals
Signals are `npm ci`, `npm run check`, `npm run fix` for style repair, and explicit Mocha invocation for `test_cli.js` and integration tests that import `test_common.js`. After dependency edits, verify that `package-lock.json` changes intentionally and that the mocked CLI tests still launch `io-engine-client` against `grpc-mock`.
