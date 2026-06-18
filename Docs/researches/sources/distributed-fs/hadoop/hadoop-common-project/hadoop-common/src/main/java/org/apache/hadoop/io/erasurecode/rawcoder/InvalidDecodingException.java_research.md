# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/InvalidDecodingException.java

Purpose: checked exception signaling that decoded outputs failed validation.

Important APIs/types/functions: public class extending `IOException`; `serialVersionUID`; constructor accepting a description string.

Control flow: no internal logic beyond passing the message to `IOException`. It is thrown by `DecodingValidator` when reconstruction comparison fails.

State and persistence: exception instance state only.

Dependencies and integration: lets validation failures flow through existing raw decoder `IOException` signatures.

Risks: because it is an `IOException`, callers may conflate validation failure with transport or native-code failures unless they catch the specific subtype. Tests should check the subtype for corrupted decode output and ensure ordinary decoder errors are not incorrectly mapped to this class.
