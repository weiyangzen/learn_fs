# sources/distributed-fs/eos/unit_tests/mgm/ConversionInfoTests.cc

## Purpose
Tests parsing and serialization of MGM conversion job descriptors. Conversion strings encode file id, target scheduling group, layout id, placement policy, app tag, and ctime-update behavior.

## Important APIs, types, and functions
The tests use `eos::mgm::ConversionInfo::parseConversionString()`, `ConversionInfo::ToString()`, `GroupLocator::parseGroup()`, and fields such as `mLid`, `mAppTag`, `mPlctPolicy`, and `mUpdateCtime`.

## Control flow
Construction tests parse valid strings with gathered/scattered/hybrid placement policy tails, optional app tags delimited by carets, and trailing `+` ctime flags. Invalid strings assert null parse results. Optional-member tests verify canonical `ToString()` ordering when app tag appears before or after placement policy.

## State and persistence
State is the parsed conversion object. The string representation is persisted or queued in proc paths, so canonicalization affects job identity and compatibility.

## Dependencies and integration points
Depends on Google Test, MGM conversion code, namespace exceptions, `GroupLocator`, and XRootD string utilities for URL/proc path construction.

## Risks and test signals
The tests protect delimiter grammar and canonical output. Risks include reserved-character handling, layout id numeric base assumptions, and URL/proc path escaping. Additional signals should cover empty policy tags, app tags containing carets, and invalid group locators.
