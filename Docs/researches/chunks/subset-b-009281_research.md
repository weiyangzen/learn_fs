# sources/test-tools/lcov/tests/xml2lcov/coverage.xml lines 2795-3373

## Scope And Purpose

This chunk is the closing portion of the Cobertura XML fixture used by the `xml2lcov` test suite. It starts inside the aggregate `<lines>` block for `org.jasig.portal.RDBMUserIdentityStore$8$1`, continues through the final classes in the `org.jasig.portal` package, and then closes `</classes>`, `</package>`, `</packages>`, and `</coverage>`.

The file is not executable code. Its purpose is to provide a realistic Cobertura 0.4-style coverage input for `sources/test-tools/lcov/bin/xml2lcov` and the shared `xml2lcovutil.py` converter. This tail chunk exercises conversion of Java inner-class names, JVM method signatures, constructor names encoded as `&lt;init&gt;`, duplicate method-level and class-level line records, branch condition metadata, mixed hit counts, all-zero coverage classes, and end-of-document handling.

## XML Structure Covered

The chunk begins at source line 2795 inside an already-open `<condition>` record for `RDBMUserIdentityStore$8$1`. From there it completes that class-level line list with uncovered line records from Java source lines 768 through 819. Several of those lines are branch-bearing records with `condition-coverage="0% (0/2)"` and a single nested `<condition number="0" type="jump" coverage="0%"/>`.

After closing `RDBMUserIdentityStore$8$1`, the chunk defines these classes:

- `org.jasig.portal.RDBMUserIdentityStore$PortalUser`, in `org/jasig/portal/RDBMUserIdentityStore.java`, with partial line coverage. Its constructor and setters are hit four times, while `getUserName` and `getDefaultUserId` are not hit.
- `org.jasig.portal.RDBMUserIdentityStore$TemplateUser`, also in `RDBMUserIdentityStore.java`, with all methods and all lines uncovered.
- `org.jasig.portal.ResourceMissingException`, with several overloaded constructors plus `getResourceURI` and `getResourceDescription`, all uncovered.
- `org.jasig.portal.UserInstance`, with a constructor and getters for person, preferences manager, and locale manager, all uncovered.
- `org.jasig.portal.UserPreferencesManager`, with a constructor and getters for person, user profile, user layout manager, and stylesheet descriptor IDs, all uncovered.
- `org.jasig.portal.UserProfile`, with multiple constructors, getters, setters, `equals`, and `toString`, all uncovered. It includes branch records on constructor line 51 and `equals` lines 198 and 200.

The chunk deliberately includes both `<methods><method><lines>...` and class-level `<lines>...` records for the same source lines. That mirrors Cobertura's data model and gives the converter enough information to derive both LCOV function records and line/branch records from the same XML subtree.

## Important APIs, Types, And Data Fields

The important "APIs" here are XML schema fields consumed by `xml2lcovutil.ProcessFile`:

- `<class name="..." filename="..." line-rate="..." branch-rate="..." complexity="...">` supplies the Java logical class name, repository-relative filename used for `SF:` output, and class-level coverage rates.
- `<method name="..." signature="..." line-rate="..." branch-rate="...">` supplies function candidates for LCOV function output. Constructors are encoded as `&lt;init&gt;`, and Java bytecode signatures such as `(Ljava/sql/Connection;)Ljava/lang/Object;` or `()I` are preserved in attributes.
- `<line number="..." hits="..." branch="false"/>` supplies ordinary DA line records.
- `<line number="..." hits="..." branch="true" condition-coverage="...">` supplies branch-capable line records.
- `<conditions><condition number="..." type="jump" coverage="..."/></conditions>` supplies per-condition metadata that the converter can map to LCOV branch records.

The classes reference Java application types only as strings inside filenames, class names, and JVM signatures. Examples include `java.sql.Connection`, `org.jasig.portal.security.IPerson`, `IUserPreferencesManager`, `IUserProfile`, `IUserLayoutManager`, and `org.jasig.portal.i18n.LocaleManager`. No Java code is loaded by this fixture.

## Control Flow Semantics For Conversion

When `xml2lcov` processes this chunk as part of the whole file, the converter walks from the document root through package, class, method, and line nodes. For each class it can open or continue an LCOV source-file section keyed by the `filename` attribute. Because several classes in this chunk share `org/jasig/portal/RDBMUserIdentityStore.java`, their method and line data should merge into one LCOV `SF:` record rather than being treated as separate physical files.

Method-level line lists provide function start and hit signals. For `PortalUser`, methods such as `getUserId`, `setUserName`, `setUserId`, and `setDefaultUserId` carry `hits="4"` and should become hit function or line records, while the uncovered getters should remain found-but-unhit. For `TemplateUser`, `ResourceMissingException`, `UserInstance`, `UserPreferencesManager`, and `UserProfile`, method records should still be emitted or counted as found even when all contained lines have zero hits.

Class-level line lists provide the aggregate line and branch records. The converter must avoid double-counting a physical line just because it appears once under a method and again under the class-level `<lines>` block. Branch-bearing line records in this chunk are all uncovered, so converted `BRDA` entries should be found with taken count `0` or equivalent not-hit representation, depending on the converter's Cobertura branch mapping.

The final closing tags are part of the test signal. A streaming or DOM parser must see a well-formed close for the package and coverage document after the last class. Truncating this chunk would make the full fixture invalid XML.

## State And Persistence Behavior

This chunk persists static fixture state in XML only. It records source paths, class names, method names, JVM signatures, line numbers, hit counts, branch flags, condition coverage strings, and coverage rates. There is no runtime mutation inside the file.

During test execution, the persistent output is generated by the converter: LCOV tracefile data derived from this XML. The shared state that matters is the merge of class fragments by physical filename. In this chunk, `RDBMUserIdentityStore.java` receives records from multiple nested classes, while `ResourceMissingException.java`, `UserInstance.java`, `UserPreferencesManager.java`, and `UserProfile.java` each receive their own sections.

The repeated method-level and class-level line records mean converter state must distinguish function discovery from line-count aggregation. Persisted LCOV output should keep one line count per source line per source file, while retaining enough function entries to represent methods with the same Java source file.

## Dependencies And Integration Points

The immediate integration is the `tests/xml2lcov` harness. The local `Makefile` registers `xml2lcov.sh`, and that script is expected to run the `xml2lcov` converter over this `coverage.xml` fixture and compare generated LCOV output against expected signals.

The fixture depends on Cobertura XML conventions rather than repository Java sources. Its root declares the Cobertura coverage DTD earlier in the file, and this chunk relies on that schema's package/class/method/line/condition shape. The converter depends on Python XML parsing plus local `xml2lcovutil.py` behavior documented elsewhere in this research tree.

Important downstream integration points are LCOV consumers that read converter output. The generated tracefile should provide `SF`, `FN`/`FNDA` or equivalent function records, `DA` line records, branch records for `branch="true"` lines, summary totals, and `end_of_record` separators in a way accepted by the broader LCOV test suite.

## Risks And Edge Cases

The chunk boundary itself is an edge case for research and merge tooling: it starts inside a nested `<condition>`/`<line>` block and not at a class or package boundary. Any chunk-level parser that assumes each chunk is standalone XML will fail; reconciliation must combine it with `subset-b-009280`.

Inner class names include dollar signs, and constructor names are XML-escaped Java bytecode names. Converter code that normalizes names too aggressively can collapse distinct methods or produce unstable function names. JVM signatures are necessary disambiguators for overloaded constructors and getters/setters with the same method name shape.

Several classes have `branch-rate="1.0"` while containing no branch-bearing lines, and others have `branch-rate="0.0"` with explicit uncovered branch lines. Tests should not infer branch records solely from the class-level branch-rate field; the actual branch records come from line-level `branch="true"` and nested conditions.

All-zero classes are intentional. A converter that suppresses classes or methods with zero hits would lose found-but-unhit functions and lines, changing LCOV `FNF`, `FNH`, `LF`, and `LH` totals.

The same physical line can appear in a method line list and in the class-level line list. Naive aggregation can double-count hits or line-found totals. This is especially visible in `PortalUser`, where line hits of `4` appear in both method and class line lists.

## Test Signals

Useful test signals from this chunk include:

- The full XML document remains well formed through the final `</coverage>` close.
- `RDBMUserIdentityStore.java` output merges records from `RDBMUserIdentityStore$8$1`, `$PortalUser`, and `$TemplateUser`.
- `PortalUser` contributes a mix of hit and unhit method/line records, including hit count `4`.
- `TemplateUser`, `ResourceMissingException`, `UserInstance`, `UserPreferencesManager`, and `UserProfile` contribute found-but-unhit coverage records.
- Branch-capable lines in the tail of `$8$1` and `UserProfile` are converted into uncovered branch records without relying on class-level branch-rate alone.
- Function discovery handles `&lt;init&gt;`, overloaded constructors, Java inner-class names containing `$`, and JVM signatures.
- Class-level duplicate line lists do not double-count LCOV line totals.
